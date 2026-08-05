# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

def read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"文件不存在: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
