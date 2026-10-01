# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB 上限，防止内存耗尽

def read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"文件不存在: {path}"
    if os.path.getsize(path) > MAX_FILE_SIZE:
        return f"文件过大（{os.path.getsize(path)} 字节），上限 {MAX_FILE_SIZE // (1024*1024)} MB"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
