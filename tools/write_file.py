# tool: {"name": "write_file", "description": "将内容写入指定路径的文件"}
import os


def write_file(path: str, content: str) -> str:
    # 路径安全校验：禁止路径遍历，限制在工作目录内
    resolved = os.path.realpath(path)
    work_dir = os.path.realpath(os.getcwd())
    if not resolved.startswith(work_dir + os.sep) and resolved != work_dir:
        return f"⚠️ 安全限制：禁止写入工作目录 ({work_dir}) 之外的文件"
    # 防止写入目录路径
    if os.path.isdir(resolved):
        return f"⚠️ {path} 是一个目录，不能写入"
    # 创建父目录（仅在工作目录内）
    parent = os.path.dirname(resolved)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(resolved, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已成功写入: {path}"
