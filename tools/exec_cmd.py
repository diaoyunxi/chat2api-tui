# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import subprocess

def exec_cmd(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except subprocess.TimeoutExpired:
        return "命令执行失败: 执行超时"
    except FileNotFoundError:
        return "命令执行失败: 命令未找到"
    except PermissionError:
        return "命令执行失败: 权限不足"
    except Exception:
        return "命令执行失败: 未知错误"
