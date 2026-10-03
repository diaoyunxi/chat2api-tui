# tool: {"name": "read_file", "description": "读取指定路径的文件内容"}
import os

# 工作目录白名单：限制 read_file 只能访问此目录下的文件，
# 防止路径遍历读取 /etc/passwd、~/.ssh/ 等敏感路径 (CWE-22)
_WORKSPACE_DIR = os.environ.get("CHAT2API_WORKSPACE_DIR", os.getcwd())

# 文件最大读取字节数，防止大文件导致 OOM (CWE-400)
MAX_READ_BYTES = 1_000_000  # 1 MB


def _validate_path(path: str) -> str:
    """
    校验路径是否在工作目录内，返回解析后的绝对路径。
    路径遍历攻击时抛出 ValueError。
    """
    # 解析为绝对路径（处理 ..、符号链接等）
    abs_path = os.path.realpath(os.path.abspath(path))
    workspace = os.path.realpath(_WORKSPACE_DIR)

    # 使用 commonpath 校验，防止前缀匹配绕过（如 /workspace-evil/）
    try:
        common = os.path.commonpath([abs_path, workspace])
    except ValueError:
        # Windows 上不同驱动器号会抛出 ValueError
        raise ValueError(f"路径不在允许的工作目录内: {path}")

    if common != workspace:
        raise ValueError(f"路径不在允许的工作目录内: {path}")

    return abs_path


def read_file(path: str) -> str:
    # 安全校验：限制在工作目录内
    try:
        abs_path = _validate_path(path)
    except ValueError as e:
        return f"⚠️ 安全限制: {e}"

    if not os.path.exists(abs_path):
        return f"文件不存在: {path}"

    if not os.path.isfile(abs_path):
        return f"不是文件: {path}"

    # 安全校验：文件大小限制
    try:
        file_size = os.path.getsize(abs_path)
    except OSError as e:
        return f"无法获取文件大小: {e}"

    if file_size > MAX_READ_BYTES:
        return (
            f"⚠️ 文件过大（{file_size} 字节），超过最大读取限制"
            f"（{MAX_READ_BYTES} 字节），拒绝读取以防止内存溢出"
        )

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        return f"⚠️ 文件不是有效的 UTF-8 文本文件: {path}"
    except PermissionError:
        return f"⚠️ 权限不足，无法读取: {path}"
    except OSError as e:
        return f"读取文件失败: {e}"
