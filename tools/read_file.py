# tool: {"name": "read_file", "description": "读取指定路径的文本文件内容，支持二进制检测和大小限制"}
import os

# 文件读取大小上限：1 MB，超过此值截断以避免 LLM 上下文溢出 (CWE-770)
MAX_READ_BYTES = 1 * 1024 * 1024


def read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"文件不存在: {path}"
    if not os.path.isfile(path):
        return f"路径不是普通文件: {path}"
    try:
        size = os.path.getsize(path)
    except OSError as e:
        return f"无法获取文件大小: {e}"

    # 二进制文件检测：读取首 8KB 探测是否存在 NUL 字节（常见于二进制/媒体/可执行文件）
    try:
        with open(path, "rb") as bf:
            head = bf.read(8192)
        if b"\x00" in head:
            return f"[二进制文件，无法读取] {path} ({size} 字节)"
    except OSError as e:
        return f"无法打开文件: {e}"

    # 超大文件提示截断
    truncated = False
    if size > MAX_READ_BYTES:
        truncated = True

    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read(MAX_READ_BYTES)
    except UnicodeDecodeError:
        # 非 UTF-8 文本（如 GBK / Latin-1），回退到宽松解码并标记替换
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(MAX_READ_BYTES)
        except OSError as e:
            return f"读取文件失败: {e}"
        suffix = "（⚠ 非 UTF-8 编码，部分字符已替换为 ?）"
        if truncated:
            suffix += f"，已截断至前 {MAX_READ_BYTES} 字节"
        return content + suffix
    except OSError as e:
        return f"读取文件失败: {e}"

    if truncated:
        content += f"\n...[已截断，文件总大小 {size} 字节，仅显示前 {MAX_READ_BYTES} 字节]"
    return content
