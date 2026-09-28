# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

# 禁止读取的敏感目录和文件
_BLOCKED_PATHS = {
    "/etc/shadow", "/etc/passwd", "/etc/sudoers",
    "/proc", "/sys", "/dev",
}
_BLOCKED_PREFIXES = ("/etc/", "/proc/", "/sys/", "/dev/")


def read_file(path: str) -> str:
    if not path or not path.strip():
        return "路径为空"

    # 解析真实路径，防止符号链接绕过
    real_path = os.path.realpath(path)

    # 限制只能读取当前工作目录下的文件
    cwd = os.path.realpath(os.getcwd())
    if not real_path.startswith(cwd + os.sep) and real_path != cwd:
        return f"安全限制: 仅允许读取当前工作目录 ({cwd}) 下的文件"

    # 黑名单校验（防御性，理论上路径限制已覆盖）
    for blocked in _BLOCKED_PREFIXES:
        if real_path.startswith(blocked):
            return f"安全限制: 禁止读取系统目录 {blocked}"
    if real_path in _BLOCKED_PATHS:
        return f"安全限制: 禁止读取 {real_path}"

    if not os.path.exists(real_path):
        return f"文件不存在: {path}"
    if not os.path.isfile(real_path):
        return f"不是文件: {path}"

    # 文件大小限制 (1MB)
    MAX_SIZE = 1 * 1024 * 1024
    if os.path.getsize(real_path) > MAX_SIZE:
        return f"文件过大（超过 1MB），拒绝读取"

    with open(real_path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()
