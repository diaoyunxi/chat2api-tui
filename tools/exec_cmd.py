# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import subprocess

# 危险 shell 元字符：出现管道、重定向、命令串联等符号时直接拒绝，防止命令注入。
# 安全考量（CWE-78 / OWASP Command Injection）：
#   1. 不使用 shell=True，改用 shlex.split 解析后以 argv 形式执行，
#      参数不会被 shell 解释，从根源上消除命令注入；
#   2. 对包含管道/重定向/串联等元字符的输入提前拒绝，
#      避免 `a | b`、`a > f`、`a && b`、反引号、$( ) 这类注入行为；
#   3. 保留超时，避免命令长时间挂起占用资源。
_DANGEROUS_TOKENS = (";", "&&", "||", "|", ">", "<", "`", "$(", "&")


def exec_cmd(command: str) -> str:
    """执行系统命令并返回输出结果。

    :param command: 待执行的命令字符串（不含 shell 元字符）
    :return: 成功时返回 stdout（存在 stderr 时同时返回），失败时返回错误信息
    """
    # 空命令直接返回提示，避免无意义调用
    if not command or not command.strip():
        return "命令为空，已忽略"

    # 拒绝包含危险 shell 元字符的命令，防止管道/重定向/命令串联注入
    for token in _DANGEROUS_TOKENS:
        if token in command:
            return f"命令被拒绝：包含不安全的 shell 元字符 {token!r}，存在命令注入风险"

    # 使用 shlex 安全拆分参数，不经过 shell 解释
    try:
        argv = shlex.split(command)
    except ValueError as e:
        return f"命令解析失败: {str(e)}"

    if not argv:
        return "命令为空，已忽略"

    try:
        result = subprocess.run(
            argv, shell=False, capture_output=True, text=True, timeout=30
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}" if result.stderr else result.stdout
    except Exception as e:
        return f"命令执行失败: {str(e)}"
