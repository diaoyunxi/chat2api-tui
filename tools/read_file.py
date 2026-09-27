# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

# 禁止读取的敏感路径前缀（CWE-73: External Control of File Name or Path）
_SENSITIVE_PATH_PREFIXES = (
    "/etc/", "/proc/", "/sys/", "/dev/",
    "/boot/", "/root/.ssh/", "/root/.gnupg/",
    os.path.expanduser("~/.ssh/"),
    os.path.expanduser("~/.gnupg/"),
)


def read_file(path: str) -> str:
    real_path = os.path.realpath(path)
    for prefix in _SENSITIVE_PATH_PREFIXES:
        if real_path.startswith(prefix):
            return f"安全限制: 禁止读取敏感路径 {prefix} 下的文件"
    if not os.path.exists(real_path):
        return f"文件不存在: {path}"
    with open(real_path, "r", encoding="utf-8") as f:
        return f.read()
