# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess


def exec_cmd(command: str) -> str:
    """安全执行系统命令。

    使用 shlex.split 拆分命令并以 shell=False 方式执行，
    防止命令注入（CWE-78）。
    """
    try:
        args = shlex.split(command)
        result = subprocess.run(
            args,
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
