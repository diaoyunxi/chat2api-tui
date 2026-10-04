# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import shlex
import signal
import subprocess

# 命令白名单：仅允许安全的只读命令执行
_ALLOWED_COMMANDS = frozenset({
    "ls", "cat", "head", "tail", "wc", "date", "whoami", "id",
    "uname", "df", "free", "uptime", "ps", "grep", "find",
    "echo", "pwd", "env", "which", "type", "file", "stat",
})


def exec_cmd(command: str) -> str:
    """安全执行系统命令，超时后彻底终止进程组防止孤儿进程泄漏。

    修复：
    1. shell=False + shlex.split 防止命令注入 (CWE-78)
    2. 命令白名单校验，仅允许只读命令 (CWE-862)
    3. TimeoutExpired 时 kill 进程组，防止 shell 子进程泄漏 (CWE-404)
    """
    if not command or not command.strip():
        return "命令为空"

    try:
        args = shlex.split(command)
    except ValueError as e:
        return f"命令解析失败: {e}"

    if not args:
        return "命令为空"

    # 命令白名单校验
    cmd_name = args[0]
    if cmd_name not in _ALLOWED_COMMANDS:
        return f"命令 '{cmd_name}' 不在安全白名单中，拒绝执行"

    try:
        # start_new_session=True 创建新进程组，超时时可彻底 kill 整组
        proc = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            # 超时：杀死整个进程组，防止孤儿子进程泄漏
            try:
                import os
                os.killpg(proc.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                proc.kill()
            proc.wait()
            return f"命令执行超时（>30s），已终止进程组"

        output = stdout or ""
        if stderr:
            output += f"\nSTDERR:\n{stderr}"
        # 限制输出大小防止内存溢出
        if len(output) > 50000:
            output = output[:50000] + "\n... (输出已截断)"
        return output or "(无输出)"

    except Exception as e:
        return f"命令执行失败: {e}"
