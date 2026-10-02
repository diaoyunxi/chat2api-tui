# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 危险命令关键词（提示性拦截）
_DANGEROUS = ("rm -rf", "rm -r ", "mkfs", "dd if=", ":(){", "> /dev/sd",
              "shutdown", "reboot", "chmod -R", "chown -R")


def exec_cmd(command: str) -> str:
    """安全执行系统命令，使用 shell=False 防止命令注入"""
    try:
        # 危险命令拦截
        normalized = " ".join(command.split()).lower().replace('"', '').replace("'", "")
        if any(d in normalized for d in _DANGEROUS):
            return f"⚠️ 出于安全考虑，疑似危险命令已被阻止执行：{command}"

        # 使用 shlex.split + shell=False 防止命令注入
        args = shlex.split(command)
        if not args:
            return "⚠️ 命令为空"
        result = subprocess.run(args, shell=False, capture_output=True, text=True, timeout=30)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except subprocess.TimeoutExpired:
        return "命令执行超时（>30s）"
    except ValueError as e:
        return f"命令解析错误：{e}"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
