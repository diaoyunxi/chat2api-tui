# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess


def exec_cmd(command: str) -> str:
    """安全执行命令：使用 shell=False + shlex.split 防止命令注入 (CWE-78)。"""
    try:
        args = shlex.split(command)
        if not args:
            return "错误: 空命令"
        result = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except FileNotFoundError:
        return f"命令未找到: {command.split()[0] if command else ''}"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
