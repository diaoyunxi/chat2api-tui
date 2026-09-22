# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 危险命令黑名单 - 禁止执行可能导致系统损害的命令
_DANGEROUS_COMMANDS = frozenset({
    "rm", "dd", "mkfs", "fdisk", "format", "shutdown", "reboot",
    "halt", "poweroff", "init", "kill", "killall", "pkill",
})


def exec_cmd(command: str) -> str:
    """执行系统命令并返回输出结果。

    Args:
        command: 要执行的 shell 命令字符串

    Returns:
        命令的标准输出（如有错误输出则一并返回）
    """
    try:
        # 安全检查：拒绝执行危险命令
        try:
            parts = shlex.split(command)
        except ValueError:
            parts = command.split()
        if parts and parts[0].rsplit("/", 1)[-1] in _DANGEROUS_COMMANDS:
            return f"安全限制: 命令 '{parts[0]}' 被拒绝执行"

        result = subprocess.run(
            command,
            shell=True,
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
        return "命令执行超时（30秒）"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
