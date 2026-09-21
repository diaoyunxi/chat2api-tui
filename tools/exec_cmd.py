# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess


def exec_cmd(command: str) -> str:
    try:
        result = subprocess.run(
            shlex.split(command),
            shell=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            if result.stderr
            else result.stdout
        )
    except Exception as e:
        return f"命令执行失败: {str(e)}"
