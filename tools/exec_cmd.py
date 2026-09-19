# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import subprocess

def exec_cmd(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, check=False)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except Exception as e:
        return f"命令执行失败: {str(e)}"
