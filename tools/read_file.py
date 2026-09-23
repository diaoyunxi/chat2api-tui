# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os


def read_file(path: str) -> str:
    # 路径安全校验：禁止路径遍历，限制在工作目录内
    resolved = os.path.realpath(path)
    work_dir = os.path.realpath(os.getcwd())
    if not resolved.startswith(work_dir + os.sep) and resolved != work_dir:
        return f"⚠️ 安全限制：禁止读取工作目录 ({work_dir}) 之外的文件"
    if not os.path.exists(resolved):
        return f"文件不存在: {path}"
    if os.path.isdir(resolved):
        return f"⚠️ {path} 是一个目录，不是文件"
    # 限制文件大小，防止内存溢出
    size = os.path.getsize(resolved)
    if size > 10 * 1024 * 1024:  # 10MB
        return f"⚠️ 文件过大 ({size / 1024 / 1024:.1f}MB)，最大允许 10MB"
    with open(resolved, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
