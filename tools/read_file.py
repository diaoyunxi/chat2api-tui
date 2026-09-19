# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

# 禁止读取的敏感路径
BLOCKED_PATHS = frozenset({
    "/etc/shadow", "/etc/gshadow",
})

# 文件大小限制 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def read_file(path: str) -> str:
    """
    读取指定路径的文件内容。

    安全措施:
    - 阻止读取系统敏感文件
    - 限制文件大小防止内存溢出
    """
    if not path or not path.strip():
        return "错误: 路径不能为空"

    abs_path = os.path.abspath(path)

    if not os.path.exists(abs_path):
        return f"文件不存在: {path}"

    if not os.path.isfile(abs_path):
        return f"不是文件: {path}"

    # 检查敏感路径
    for blocked in BLOCKED_PATHS:
        if abs_path.startswith(blocked):
            return f"错误: 禁止读取敏感文件: {blocked}"

    # 检查文件大小
    file_size = os.path.getsize(abs_path)
    if file_size > MAX_FILE_SIZE:
        return f"错误: 文件过大 ({file_size / 1024 / 1024:.1f}MB > 10MB)"

    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except PermissionError:
        return f"权限不足，无法读取: {path}"
    except OSError as e:
        return f"读取失败: {e}"
