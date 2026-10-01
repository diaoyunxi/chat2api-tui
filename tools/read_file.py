# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os
import logging

logger = logging.getLogger("read_file")

# 工作目录白名单：仅允许读取当前工作目录及其子目录下的文件
def _is_within_workspace(path: str) -> bool:
    """校验路径是否在当前工作目录内，防止路径遍历攻击 (CWE-22)"""
    try:
        real_path = os.path.realpath(path)
        cwd = os.path.realpath(os.getcwd())
        return real_path.startswith(cwd + os.sep) or real_path == cwd
    except (ValueError, OSError):
        return False

def read_file(path: str) -> str:
    # 路径遍历防护 (CWE-22, CWE-73)
    if not _is_within_workspace(path):
        logger.warning("拒绝读取工作目录外的文件: %s", path)
        return "错误：不允许读取工作目录外的文件"
    if not os.path.exists(path):
        return f"文件不存在: {path}"
    # 文件大小限制：防止 LLM 上下文溢出 (CWE-770)
    MAX_FILE_SIZE = 100 * 1024  # 100 KB
    try:
        if os.path.getsize(path) > MAX_FILE_SIZE:
            return f"文件过大 ({os.path.getsize(path)} bytes)，上限 {MAX_FILE_SIZE} bytes"
    except OSError:
        pass
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except UnicodeDecodeError:
        return "错误：该文件不是文本文件（可能是二进制格式）"
