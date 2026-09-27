# tool: {"name": "write_file", "description": "将内容写入指定路径的文件"}
import os

# 禁止写入的敏感路径前缀（CWE-73: External Control of File Name or Path）
_SENSITIVE_PATH_PREFIXES = (
    "/etc/", "/proc/", "/sys/", "/dev/",
    "/boot/", "/root/.ssh/", "/root/.gnupg/",
    os.path.expanduser("~/.ssh/"),
    os.path.expanduser("~/.gnupg/"),
)


def write_file(path: str, content: str) -> str:
    abs_path = os.path.abspath(path)
    # 路径安全校验：拒绝写入系统敏感目录
    if any(abs_path.startswith(prefix) for prefix in _SENSITIVE_PATH_PREFIXES):
        return f"错误：禁止写入敏感路径 {path}"
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"已成功写入: {abs_path}"
