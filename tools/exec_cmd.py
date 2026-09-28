# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import os
import shlex
import subprocess

# 允许执行的命令白名单（仅允许安全的只读命令）
ALLOWED_COMMANDS = frozenset({
    "ls", "cat", "echo", "pwd", "whoami", "hostname", "date", "uname",
    "head", "tail", "wc", "sort", "uniq", "cut", "tr", "diff", "grep",
    "which", "file", "stat", "du", "df", "free", "ps", "env", "id",
    "uptime", "python", "python3", "pip", "node", "git",
})

# 禁止的 shell 元字符（防止注入）
_BLOCKED_META = set('|;`$()>&<\n')

# 命令最大长度
MAX_CMD_LENGTH = 512


def exec_cmd(command: str) -> str:
    """安全执行白名单内的命令并返回输出。

    安全措施:
    - 命令白名单（仅允许只读型命令）
    - shell=False 防止注入
    - 元字符检查
    - 长度限制
    """
    if not command or not command.strip():
        return "命令为空"

    cmd = command.strip()

    # 长度限制
    if len(cmd) > MAX_CMD_LENGTH:
        return f"命令过长（{len(cmd)} 字符），最大允许 {MAX_CMD_LENGTH} 字符"

    # 元字符检查
    for ch in cmd:
        if ch in _BLOCKED_META:
            return f"命令包含禁止的特殊字符 '{ch}'，拒绝执行"

    # 解析命令
    try:
        tokens = shlex.split(cmd)
    except ValueError as e:
        return f"命令解析失败: {e}"

    if not tokens:
        return "命令为空"

    # 白名单校验（取基础命令名）
    base_cmd = os.path.basename(tokens[0])
    if base_cmd not in ALLOWED_COMMANDS:
        return f"命令 '{base_cmd}' 不在安全白名单中，拒绝执行"

    try:
        result = subprocess.run(
            tokens,
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
        return "命令执行超时（30秒）"
    except FileNotFoundError:
        return f"命令未找到: {base_cmd}"
    except Exception as e:
        return f"命令执行失败: {e}"
