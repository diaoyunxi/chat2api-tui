#!/usr/bin/env python3
# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

def read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"文件不存在: {path}"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except PermissionError:
        return "读取失败: 权限不足"
    except UnicodeDecodeError:
        return "读取失败: 文件不是有效的文本文件"
    except Exception as e:
        return f"读取失败: {type(e).__name__}"
