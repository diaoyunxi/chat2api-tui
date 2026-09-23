# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess


def exec_cmd(command: str) -> str:
    """执行系统命令，使用 shell=False 防止命令注入"""
    try:
        args = shlex.split(command)
        result = subprocess.run(args, capture_output=True, text=True, timeout=30)
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        return output
    except FileNotFoundError:
        return f"命令未找到: {args[0] if args else command}"
    except subprocess.TimeoutExpired:
        return "命令执行超时（30秒）"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
