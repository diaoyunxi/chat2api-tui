#!/usr/bin/env python3
# tool: {"name": "write_file", "description": "将内容写入指定路径的文件"}
import os

def write_file(path: str, content: str) -> str:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"已成功写入: {path}"
    except PermissionError:
        return "写入失败: 权限不足"
    except OSError as e:
        return f"写入失败: {type(e).__name__}"
