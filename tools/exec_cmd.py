# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import subprocess
import shlex

# 命令白名单：仅允许安全的只读命令
ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "wc", "grep", "find", "echo",
    "date", "whoami", "hostname", "uname", "pwd", "df", "du",
    "ps", "top", "free", "uptime", "env", "which", "type",
    "python3", "python", "pip", "git",
}


def _is_command_allowed(command: str) -> bool:
    """检查命令是否在白名单中"""
    try:
        parts = shlex.split(command)
    except ValueError:
        return False
    if not parts:
        return False
    # 取第一个 token 作为命令名
    cmd_name = parts[0].split("/")[-1]
    return cmd_name in ALLOWED_COMMANDS


def exec_cmd(command: str) -> str:
    """执行系统命令并返回输出结果。仅允许白名单内的安全命令。"""
    if not _is_command_allowed(command):
        return f"命令被拒绝: '{command}' 不在允许的命令列表中。允许的命令: {', '.join(sorted(ALLOWED_COMMANDS))}"
    try:
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except subprocess.TimeoutExpired:
        return "命令执行超时 (30秒)"
    except Exception as e:
        return f"命令执行失败: {e!s}"
