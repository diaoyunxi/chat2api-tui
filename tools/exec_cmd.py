# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 命令白名单：仅允许安全命令
ALLOWED_COMMANDS = frozenset({
    "ls", "cat", "echo", "pwd", "whoami", "hostname", "date", "uname",
    "head", "tail", "wc", "sort", "uniq", "cut", "tr", "diff", "find",
    "grep", "which", "file", "stat", "du", "df", "free", "ps", "env",
    "id", "uptime", "python", "python3", "pip", "pip3", "node", "npm",
    "git", "curl", "wget", "ping",
})

MAX_COMMAND_LENGTH = 1000

def exec_cmd(command: str) -> str:
    """安全执行白名单内的命令，使用 shell=False 防止命令注入"""
    if not command or not command.strip():
        return "命令为空"
    if len(command) > MAX_COMMAND_LENGTH:
        return f"命令长度超过限制 ({MAX_COMMAND_LENGTH} 字符)"

    try:
        parts = shlex.split(command)
    except ValueError as e:
        return f"命令解析失败: {e}"

    if not parts:
        return "命令为空"

    import os
    base_cmd = os.path.basename(parts[0])
    if base_cmd not in ALLOWED_COMMANDS:
        return f"命令 '{base_cmd}' 不在安全白名单中，拒绝执行"

    try:
        result = subprocess.run(
            parts,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output if output else "(无输出)"
    except subprocess.TimeoutExpired:
        return "命令执行超时 (30秒)"
    except FileNotFoundError:
        return f"命令未找到: {parts[0]}"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
