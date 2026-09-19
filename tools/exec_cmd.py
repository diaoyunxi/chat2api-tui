# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 危险命令黑名单 - 禁止执行可能造成系统破坏的命令
BLOCKED_COMMANDS = frozenset({
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=/dev/zero",
    ":(){:|:&};:", "chmod -R 777 /", "shutdown", "reboot",
    "init 0", "init 6", "halt", "poweroff",
})


def exec_cmd(command: str) -> str:
    """
    执行系统命令并返回输出结果。

    安全措施:
    - 使用 shlex 解析命令，避免 shell 注入
    - 禁止执行黑名单中的危险命令
    - 限制执行超时为 30 秒
    """
    if not command or not command.strip():
        return "错误: 命令不能为空"

    cmd_stripped = command.strip()

    # 检查危险命令
    cmd_lower = cmd_stripped.lower()
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd_lower:
            return f"错误: 检测到危险命令，已阻止执行: {blocked}"

    try:
        # 使用 shlex 解析命令为列表，避免 shell 注入
        cmd_parts = shlex.split(cmd_stripped)
        if not cmd_parts:
            return "错误: 命令解析后为空"

        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output if output.strip() else "(命令执行成功，无输出)"
    except FileNotFoundError:
        return f"错误: 命令不存在: {cmd_parts[0] if cmd_parts else command}"
    except subprocess.TimeoutExpired:
        return "错误: 命令执行超时 (30秒)"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
