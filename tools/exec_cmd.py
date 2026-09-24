# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果（安全沙箱模式）"}
import os
import shlex
import subprocess

# 危险命令黑名单
DANGEROUS_COMMANDS = [
    "rm -rf /", "rm -rf /*", "mkfs", "dd if=", ":(){ :|:& };:",
    "> /dev/sda", "chmod -R 777 /", "shutdown", "reboot", "halt",
    "poweroff", "init 0", "init 6",
]

# 允许执行的命令白名单（基于首个 token）
ALLOWED_COMMANDS = {
    "ls", "cat", "echo", "pwd", "whoami", "hostname", "date", "uname",
    "head", "tail", "wc", "sort", "uniq", "cut", "tr", "diff", "find",
    "grep", "which", "whereis", "file", "stat", "du", "df", "free",
    "ps", "env", "id", "uptime", "ping", "nslookup", "dig",
    "python", "python3", "pip", "pip3", "node", "npm", "git",
    "curl", "wget", "mkdir", "touch", "cp", "mv", "ln",
    "tar", "zip", "unzip", "gzip", "gunzip", "sed", "awk",
    "basename", "dirname", "realpath", "tee", "seq", "test",
}

MAX_COMMAND_LENGTH = 1000


def exec_cmd(command: str) -> str:
    """安全执行系统命令并返回输出结果。

    安全措施：
    1. 命令长度限制（1000 字符）
    2. 危险命令黑名单
    3. 命令白名单机制（仅允许安全命令）
    4. 使用 shell=False + shlex.split() 防止命令注入
    """
    # 命令长度校验
    if len(command) > MAX_COMMAND_LENGTH:
        return f"安全限制: 命令长度超过 {MAX_COMMAND_LENGTH} 字符"

    cmd_lower = command.lower().strip()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous.lower() in cmd_lower:
            return f"安全限制: 命令包含危险操作 '{dangerous}'"

    # 解析命令并检查白名单
    try:
        tokens = shlex.split(command)
    except ValueError as e:
        return f"命令解析失败: {e}"

    if not tokens:
        return "命令为空"

    base_cmd = os.path.basename(tokens[0])
    if base_cmd not in ALLOWED_COMMANDS:
        return f"安全限制: 命令 '{base_cmd}' 不在允许的白名单中"

    # 使用 shell=False 防止命令注入
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
        return output
    except subprocess.TimeoutExpired:
        return "命令执行超时 (30 秒)"
    except FileNotFoundError:
        return f"命令未找到: {tokens[0]}"
    except Exception as e:
        return f"命令执行失败: {e}"
