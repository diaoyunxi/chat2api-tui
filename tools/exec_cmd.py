# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 危险命令关键词黑名单（基础防护）
_BLOCKED = (
    "rm -rf", "rm -r ", "mkfs", "dd if=", ":(){", "> /dev/sd",
    "shutdown", "reboot", "chmod -R", "chown -R", "curl|sh",
    "wget|sh", "eval(", "exec(",
)

def exec_cmd(command: str) -> str:
    """执行系统命令并返回输出结果。
    
    安全改进：
    - 使用 shlex.split() 解析命令，避免 shell=True 注入风险
    - 对危险命令关键词进行拦截
    - 保留超时保护
    """
    cmd_lower = command.lower().strip()
    for pattern in _BLOCKED:
        if pattern in cmd_lower:
            return f"⚠️ 出于安全考虑，疑似危险命令已被阻止执行: {command}"

    try:
        args = shlex.split(command)
        if not args:
            return "错误: 命令为空"
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
    except FileNotFoundError:
        return f"命令未找到: {command.split()[0] if command.split() else command}"
    except subprocess.TimeoutExpired:
        return f"命令执行超时 (>30s): {command}"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
