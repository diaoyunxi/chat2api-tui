# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import re
import shlex
import subprocess

# Whitelist of allowed base commands (safe, read-only operations)
ALLOWED_COMMANDS = frozenset({
    "ls", "cat", "df", "ps", "uptime", "free", "head", "tail",
    "grep", "wc", "date", "whoami", "id", "uname", "echo",
    "pwd", "which", "type", "file", "stat",
})

# Block dangerous shell metacharacters
_BLOCKED_META = re.compile(r'[|;`$()>&<]')


def _validate_command(command: str) -> str | None:
    """Validate command against whitelist. Returns error message or None if safe."""
    if not command or not command.strip():
        return "命令不能为空"

    if _BLOCKED_META.search(command):
        return "命令包含不允许的 shell 元字符（管道、重定向、命令替换等）"

    try:
        parts = shlex.split(command)
    except ValueError:
        return "命令格式不合法"

    if not parts:
        return "命令不能为空"

    base_cmd = parts[0]
    if base_cmd not in ALLOWED_COMMANDS:
        allowed = ", ".join(sorted(ALLOWED_COMMANDS))
        return f"命令 '{base_cmd}' 不在白名单中。允许的命令: {allowed}"

    return None


def exec_cmd(command: str) -> str:
    """Execute a whitelisted read-only command and return its output."""
    error = _validate_command(command)
    if error:
        return f"命令被拒绝: {error}"

    try:
        parts = shlex.split(command)
        result = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output if output else "(无输出)"
    except subprocess.TimeoutExpired:
        return "命令执行超时 (30s)"
    except Exception as e:
        return f"命令执行失败: {e}"
