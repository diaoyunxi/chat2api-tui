# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import os
import shlex
import subprocess

# 允许执行的命令白名单（仅允许安全的只读/信息查询命令）
_ALLOWED_COMMANDS = frozenset({
    "ls", "cat", "head", "tail", "wc", "grep", "find",
    "date", "whoami", "id", "uname", "hostname",
    "df", "du", "free", "uptime", "ps", "top",
    "echo", "pwd", "which", "type", "file",
    "python3", "python", "pip", "node", "npm",
    "git", "curl", "wget",
})

# 明确禁止的危险命令模式
_BLOCKED_PATTERNS = [
    "rm -rf", "mkfs", "dd if=", "chmod -R 777",
    "shutdown", "reboot", "halt", "poweroff",
    ":(){ :|:& };:", "> /dev/sda",
]


def _validate_command(command: str) -> tuple:
    """校验命令是否在白名单内，返回 (allowed: bool, reason: str)。"""
    if not command or not command.strip():
        return False, "命令为空"

    cmd_lower = command.lower()
    for pattern in _BLOCKED_PATTERNS:
        if pattern in cmd_lower:
            return False, f"命令包含危险模式: {pattern}"

    try:
        parts = shlex.split(command)
    except ValueError as e:
        return False, f"命令解析失败: {e}"

    if not parts:
        return False, "命令为空"

    base_cmd = os.path.basename(parts[0])
    if base_cmd not in _ALLOWED_COMMANDS:
        return False, f"命令 '{base_cmd}' 不在安全白名单中（允许: {', '.join(sorted(_ALLOWED_COMMANDS)[:10])}...）"

    return True, ""


def exec_cmd(command: str) -> str:
    """安全执行系统命令。

    使用 shlex.split 拆分命令并以 shell=False 方式执行，
    同时通过命令白名单限制可执行的命令范围，防止 AI Agent
    执行任意系统命令 (CWE-78)。
    """
    allowed, reason = _validate_command(command)
    if not allowed:
        return f"⚠️ 命令被拒绝: {reason}"

    try:
        args = shlex.split(command)
        result = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            if result.stderr
            else result.stdout
        )
    except subprocess.TimeoutExpired:
        return "⚠️ 命令执行超时（>30s）"
    except FileNotFoundError:
        return f"命令不存在: {shlex.split(command)[0] if command else '(空)'}"
    except Exception as e:
        return f"命令执行失败: {e}"
