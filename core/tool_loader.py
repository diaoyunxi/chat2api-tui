"""外置工具热加载器：扫描 tools/ 目录，解析文件头部注释，动态导入"""
import os
import sys
import json
import uuid
import importlib.util
import inspect
from typing import Dict, Any, Callable, Optional

class ToolLoader:
    def __init__(self, tools_dir: str = "tools"):
        self.tools_dir = tools_dir
        self._cache: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict] = {}
        self._sys_module_names: Dict[str, str] = {}  # tool_name -> sys.modules key
        self.load_all()

    def _parse_header(self, filepath: str) -> Optional[Dict]:
        """读取文件头部 # tool: {...} 注释"""
        with open(filepath, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if line.startswith("# tool:"):
                    try:
                        return json.loads(line[7:].strip())
                    except:
                        return None
                if not line.startswith("#") and line != "":
                    break
        return None

    def load_all(self):
        """扫描并加载所有工具模块"""
        if not os.path.exists(self.tools_dir):
            return
        for filename in os.listdir(self.tools_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                self._load_tool(os.path.join(self.tools_dir, filename))

    def _load_tool(self, filepath: str):
        """动态加载单个工具"""
        # 解析头部声明（先解析再导入，避免导入失败的工具污染 sys.modules）
        meta = self._parse_header(filepath)
        if not meta:
            return

        tool_name = meta.get("name")
        if not tool_name:
            return

        # 使用唯一模块名防止 sys.modules 覆盖冲突 (CWE-772)
        module_name = f"chat2api_tool_{tool_name}_{uuid.uuid4().hex[:8]}"
        spec = importlib.util.spec_from_file_location(module_name, filepath)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # 查找函数（约定与 tool_name 同名或第一个函数）
        func = getattr(module, tool_name, None)
        if not func:
            for attr in dir(module):
                if not attr.startswith("_") and callable(getattr(module, attr)):
                    func = getattr(module, attr)
                    break
        if not func:
            # 清理解析成功但未找到函数的模块
            sys.modules.pop(module_name, None)
            return

        # 自动生成 JSON Schema
        sig = inspect.signature(func)
        properties = {}
        required = []
        for name, param in sig.parameters.items():
            p_type = "string"
            if param.annotation is int:
                p_type = "integer"
            elif param.annotation is float:
                p_type = "number"
            elif param.annotation is bool:
                p_type = "boolean"
            properties[name] = {"type": p_type, "description": f"参数 {name}"}
            if param.default == inspect.Parameter.empty:
                required.append(name)

        self._schemas[tool_name] = {
            "type": "function",
            "function": {
                "name": tool_name,
                "description": meta.get("description", ""),
                "parameters": {"type": "object", "properties": properties, "required": required}
            }
        }
        self._cache[tool_name] = func
        self._sys_module_names[tool_name] = module_name

    def get_tools_schema(self) -> list:
        """返回所有工具的 OpenAI 格式 Schema 列表"""
        return list(self._schemas.values())

    def execute(self, tool_name: str, arguments: dict) -> str:
        """执行工具并返回字符串结果"""
        if tool_name not in self._cache:
            return f"错误：工具 {tool_name} 未找到"
        try:
            result = self._cache[tool_name](**arguments)
            return str(result) if result is not None else "执行成功（无返回值）"
        except Exception as e:
            return f"工具执行错误: {str(e)}"

    def reload(self):
        """热加载：清空缓存并重新加载，同时清理 sys.modules 防止泄漏 (CWE-772)"""
        # 清理旧的动态模块引用
        for sys_mod_name in self._sys_module_names.values():
            sys.modules.pop(sys_mod_name, None)
        self._sys_module_names.clear()
        self._cache.clear()
        self._schemas.clear()
        self.load_all()
