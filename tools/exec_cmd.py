# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess


def exec_cmd(command: str) -> str:
    try:
        # 使用 shell=False + shlex.split 防止 shell 元字符被解释 (CWE-78)
        args = shlex.split(command)
        if not args:
            return "错误：命令为空"
        result = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except ValueError as e:
        return f"命令格式错误: {e}"
    except subprocess.TimeoutExpired:
        return "命令执行超时（30 秒）"
    except FileNotFoundError:
        return f"命令不存在: {command.split()[0] if command else '(empty)'}"
    except Exception as e:
        return f"命令执行失败: {e}"
