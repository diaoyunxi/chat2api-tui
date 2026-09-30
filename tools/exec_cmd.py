# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import subprocess
import shlex

# 命令白名单：仅允许以下安全命令执行
ALLOWED_COMMANDS = {
    "ls", "cat", "echo", "pwd", "whoami", "hostname", "date", "uname",
    "head", "tail", "wc", "sort", "uniq", "grep", "find", "diff",
    "python", "python3", "pip", "pip3", "node", "npm", "git",
    "curl", "wget", "ping", "which", "file", "stat", "du", "df",
    "free", "ps", "env", "id", "mkdir", "touch", "cp", "mv",
}

# 命令最大长度限制
MAX_COMMAND_LENGTH = 1000

# 输出最大字符数
MAX_OUTPUT_LENGTH = 50000


def exec_cmd(command: str) -> str:
    """执行系统命令并返回输出结果。

    安全措施 (CWE-78)：
    1. 命令白名单机制：仅允许预定义的安全命令
    2. 使用 shell=False + shlex.split 防止命令注入
    3. 命令长度限制防止参数溢出
    4. 输出大小截断防止内存溢出
    """
    try:
        # 命令长度校验
        if len(command) > MAX_COMMAND_LENGTH:
            return f"命令长度超过限制 ({MAX_COMMAND_LENGTH} 字符)"

        # 解析命令并校验白名单
        tokens = shlex.split(command)
        if not tokens:
            return "命令为空"

        base_cmd = tokens[0].split("/")[-1]  # 去掉路径前缀
        if base_cmd not in ALLOWED_COMMANDS:
            return f"安全限制: 命令 '{base_cmd}' 不在允许的白名单中"

        # 使用 shell=False + 参数列表防止命令注入
        result = subprocess.run(
            tokens, shell=False, capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"

        # 截断过长输出
        if len(output) > MAX_OUTPUT_LENGTH:
            output = output[:MAX_OUTPUT_LENGTH] + f"\n... (输出已截断，共 {len(output)} 字符)"

        return output
    except subprocess.TimeoutExpired:
        return "命令执行超时 (30s)"
    except ValueError as e:
        return f"命令解析失败: {e}"
    except Exception as e:
        return f"命令执行失败: {e}"
