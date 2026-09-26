# tool: {"name": "exec_cmd", "description": "执行安全的系统命令并返回输出结果"}
import shlex
import subprocess

ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "wc", "grep", "find",
    "echo", "date", "uptime", "df", "free", "ps", "whoami",
    "uname", "python", "python3", "pip", "node", "npm",
}

def exec_cmd(command: str) -> str:
    try:
        parts = shlex.split(command)
        if not parts:
            return "错误: 命令为空"
        cmd_name = parts[0].split("/")[-1]
        if cmd_name not in ALLOWED_COMMANDS:
            return f"错误: 命令 '{cmd_name}' 不在允许列表中。允许的命令: {', '.join(sorted(ALLOWED_COMMANDS))}"
        result = subprocess.run(
            parts, capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output if output else "(命令执行成功，无输出)"
    except subprocess.TimeoutExpired:
        return "错误: 命令执行超时 (30秒)"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
