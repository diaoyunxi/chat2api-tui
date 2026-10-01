# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 命令白名单：仅允许安全命令
ALLOWED_COMMANDS = {"ls", "cat", "head", "tail", "wc", "grep", "find", "pwd", "date", "whoami", "echo", "tree", "file", "stat"}

def exec_cmd(command: str) -> str:
    """安全执行命令：使用 shell=False + shlex.split + 命令白名单"""
    try:
        args = shlex.split(command)
        if not args:
            return "错误：空命令"
        cmd_name = args[0].split("/")[-1]
        if cmd_name not in ALLOWED_COMMANDS:
            return f"错误：命令 '{cmd_name}' 不在白名单中。允许的命令：{', '.join(sorted(ALLOWED_COMMANDS))}"
        result = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=30)
        output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
        # 限制输出大小防止上下文溢出
        if len(output) > 50000:
            output = output[:50000] + "\n... [输出已截断]"
        return output
    except subprocess.TimeoutExpired:
        return "命令执行超时（30秒）"
    except Exception as e:
        return "命令执行失败"  # 不暴露内部错误信息
