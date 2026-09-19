# tool: {"name": "write_file", "description": "将内容写入指定路径的文件"}
import os

# 禁止写入的敏感路径
BLOCKED_PATHS = frozenset({
    "/etc/passwd", "/etc/shadow", "/etc/sudoers",
    "/boot", "/proc", "/sys", "/dev",
})


def write_file(path: str, content: str) -> str:
    """
    将内容写入指定路径的文件。

    安全措施:
    - 阻止写入系统关键路径
    - 自动创建父目录
    """
    if not path or not path.strip():
        return "错误: 路径不能为空"

    # 规范化路径
    abs_path = os.path.abspath(path)

    # 检查敏感路径
    for blocked in BLOCKED_PATHS:
        if abs_path.startswith(blocked):
            return f"错误: 禁止写入系统关键路径: {blocked}"

    try:
        parent_dir = os.path.dirname(abs_path)
        os.makedirs(parent_dir, exist_ok=True)
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"已成功写入: {abs_path}"
    except OSError as e:
        return f"写入失败: {e}"
