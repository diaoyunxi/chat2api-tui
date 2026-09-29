# tool: {"name": "write_file", "description": "将内容写入指定路径的文件"}
import os
import tempfile

# 允许写入的目录白名单（工作目录及其子目录）
_ALLOWED_BASE_DIRS = [
    os.getcwd(),
    tempfile.gettempdir(),
]


def _is_path_allowed(path: str) -> bool:
    """校验路径是否在允许的目录范围内，防止写入系统敏感文件 (CWE-73)。"""
    abs_path = os.path.realpath(os.path.abspath(path))
    for allowed_dir in _ALLOWED_BASE_DIRS:
        allowed_real = os.path.realpath(allowed_dir)
        if abs_path.startswith(allowed_real + os.sep) or abs_path == allowed_real:
            return True
    return False


def write_file(path: str, content: str) -> str:
    if not _is_path_allowed(path):
        return f"⚠️ 安全限制：不允许写入路径 {path}（仅允许写入当前工作目录和临时目录下的文件）"
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已成功写入: {path}"
