# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

# 沙箱根目录：限制文件读写仅允许在当前工作目录及其子目录内
_SANDBOX_ROOT = os.path.realpath(os.environ.get("TOOL_SANDBOX_DIR", os.getcwd()))


def _validate_path(path: str) -> str:
    """校验路径是否在沙箱范围内，返回绝对路径；越界时抛出 ValueError"""
    real_path = os.path.realpath(os.path.expanduser(path))
    if not real_path.startswith(_SANDBOX_ROOT + os.sep) and real_path != _SANDBOX_ROOT:
        raise ValueError(f"路径越界: 不允许访问沙箱目录之外的文件 ({path})")
    return real_path


def read_file(path: str) -> str:
    try:
        safe_path = _validate_path(path)
    except ValueError as e:
        return f"错误: {e}"
    if not os.path.exists(safe_path):
        return f"文件不存在: {path}"
    with open(safe_path, "r", encoding="utf-8") as f:
        return f.read()
