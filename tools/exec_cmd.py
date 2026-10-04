# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess


# 命令白名单：仅允许以下安全命令执行
ALLOWED_COMMANDS = frozenset({
    "ls", "cat", "head", "tail", "wc", "grep", "find", "date",
    "whoami", "uname", "df", "free", "ps", "uptime", "echo",
    "pwd", "env", "which", "type", "file", "stat",
})


def _validate_command(command: str) -> tuple[bool, str]:
    """校验命令安全性，拒绝危险命令和注入尝试。

    Returns:
        (allowed, reason) - allowed=True 表示可执行，reason 为拒绝原因
    """
    if not command or not command.strip():
        return False, "命令为空"

    cmd = command.strip()

    # 检查危险 shell 元字符（管道、重定向、命令替换等）
    dangerous_chars = set("|;&`$()><\n\r")
    found = [c for c in cmd if c in dangerous_chars]
    if found:
        return False, f"命令包含危险字符: {found}"

    # 使用 shlex 安全拆分参数
    try:
        parts = shlex.split(cmd)
    except ValueError as e:
        return False, f"命令解析失败: {e}"

    if not parts:
        return False, "命令解析后为空"

    # 提取实际命令名（跳过 sudo）
    cmd_name = parts[0]
    if cmd_name == "sudo" and len(parts) > 1:
        # 跳过 sudo 及其选项参数
        i = 1
        while i < len(parts) and parts[i].startswith("-"):
            if parts[i] in ("-u", "--user") and i + 1 < len(parts):
                i += 2
            else:
                i += 1
        if i >= len(parts):
            return False, "sudo 后缺少实际命令"
        cmd_name = parts[i]

    # 取 basename 防止路径绕过
    import os
    cmd_name = os.path.basename(cmd_name)

    if cmd_name not in ALLOWED_COMMANDS:
        return False, f"命令 '{cmd_name}' 不在安全白名单中"

    return True, ""


def exec_cmd(command: str) -> str:
    """安全执行系统命令并返回输出结果。

    使用 shell=False + shlex.split 杜绝命令注入 (CWE-78)。
    仅允许白名单内的安全命令执行。
    """
    allowed, reason = _validate_command(command)
    if not allowed:
        return f"[命令被拒绝] {reason}"

    try:
        parts = shlex.split(command.strip())
        result = subprocess.run(
            parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.stderr:
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        return result.stdout
    except subprocess.TimeoutExpired:
        return "命令执行超时 (30秒)"
    except FileNotFoundError:
        return f"命令不存在: {parts[0]}"
    except Exception as e:
        return f"命令执行失败: {e}"
