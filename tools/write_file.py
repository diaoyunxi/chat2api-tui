# tool: {"name": "write_file", "description": "将内容写入指定路径的文件"}
import os

# 工作目录白名单：限制 write_file 只能写入此目录下的文件，
# 防止写入系统关键路径（如 /etc/crontab、~/.ssh/authorized_keys）(CWE-73)
_WORKSPACE_DIR = os.environ.get("CHAT2API_WORKSPACE_DIR", os.getcwd())


def _validate_path(path: str) -> str:
    """
    校验路径是否在工作目录内，返回解析后的绝对路径。
    路径遍历攻击时抛出 ValueError。
    """
    abs_path = os.path.realpath(os.path.abspath(path))
    workspace = os.path.realpath(_WORKSPACE_DIR)

    try:
        common = os.path.commonpath([abs_path, workspace])
    except ValueError:
        raise ValueError(f"路径不在允许的工作目录内: {path}")

    if common != workspace:
        raise ValueError(f"路径不在允许的工作目录内: {path}")

    return abs_path


def write_file(path: str, content: str) -> str:
    # 安全校验：限制在工作目录内
    try:
        abs_path = _validate_path(path)
    except ValueError as e:
        return f"⚠️ 安全限制: {e}"

    # 创建父目录
    parent_dir = os.path.dirname(abs_path)
    if not parent_dir:
        return "⚠️ 无效的写入路径"

    try:
        os.makedirs(parent_dir, exist_ok=True)
    except PermissionError:
        return f"⚠️ 权限不足，无法创建目录: {parent_dir}"
    except OSError as e:
        return f"⚠️ 创建目录失败: {e}"

    # 写入文件
    try:
        with open(abs_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"已成功写入: {path}"
    except PermissionError:
        return f"⚠️ 权限不足，无法写入: {path}"
    except OSError as e:
        return f"⚠️ 写入文件失败: {e}"
