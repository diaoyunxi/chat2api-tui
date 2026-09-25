# tool: {"name": "write_file", "description": "将内容写入指定路径的文件"}
import os

def write_file(path: str, content: str) -> str:
    # 修复：当 path 为裸文件名（如 "file.txt"）时，os.path.dirname 返回空字符串，
    # os.makedirs("") 会抛出 FileNotFoundError
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已成功写入: {path}"
