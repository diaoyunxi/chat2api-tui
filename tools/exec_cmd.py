#!/usr/bin/env python3
# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 危险命令黑名单（匹配命令首 token 或关键子串）
_DANGEROUS_PATTERNS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=",
    ":(){ :|:& };:", "chmod -R 777 /", "shutdown",
    "reboot", "halt", "poweroff", "init 0", "init 6",
]

# 命令白名单（基于首个 token 的基础命令名）
_ALLOWED_COMMANDS = {
    "ls", "cat", "echo", "pwd", "whoami", "date", "uname",
    "head", "tail", "wc", "sort", "uniq", "cut", "tr", "diff",
    "grep", "which", "file", "stat", "du", "df", "free", "ps",
    "python", "python3", "pip", "pip3", "node", "npm", "git",
    "curl", "wget", "ping", "ifconfig", "ip", "hostname",
    "find", "mkdir", "touch", "cp", "mv", "tree", "env", "id",
}


def exec_cmd(command: str) -> str:
    """安全执行系统命令并返回输出结果。

    安全措施：
    1. 使用 shell=False + shlex.split() 防止命令注入
    2. 命令白名单机制，仅允许预定义的安全命令
    3. 危险命令模式过滤
    4. 超时控制（30 秒）
    """
    if not command or not command.strip():
        return "命令为空"

    # 危险命令模式检查
    cmd_lower = command.lower().strip()
    for pattern in _DANGEROUS_PATTERNS:
        if pattern in cmd_lower:
            return f"命令被拒绝：包含危险操作模式"

    # 使用 shlex 安全解析命令参数
    try:
        args = shlex.split(command)
    except ValueError as e:
        return f"命令解析失败: {e}"

    if not args:
        return "命令为空"

    # 白名单校验：取首个 token 的基础命令名（去掉路径前缀）
    import os
    base_cmd = os.path.basename(args[0])
    if base_cmd not in _ALLOWED_COMMANDS:
        return f"命令 '{base_cmd}' 不在允许的白名单中，拒绝执行"

    try:
        result = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except subprocess.TimeoutExpired:
        return "命令执行超时（30 秒）"
    except FileNotFoundError:
        return f"命令未找到: {args[0]}"
    except Exception as e:
        return f"命令执行失败: {type(e).__name__}"
