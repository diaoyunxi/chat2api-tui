# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import subprocess

# 输出大小上限：防止 LLM 上下文被大量输出撑爆 (CWE-770)
_MAX_OUTPUT_BYTES = 50_000


def exec_cmd(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        # 截断过大的输出，防止 LLM token 溢出
        if len(stdout) > _MAX_OUTPUT_BYTES:
            stdout = stdout[:_MAX_OUTPUT_BYTES] + f"\n... (输出已截断，原始大小 {len(result.stdout)} 字符)"
        if len(stderr) > _MAX_OUTPUT_BYTES:
            stderr = stderr[:_MAX_OUTPUT_BYTES] + f"\n... (错误输出已截断，原始大小 {len(result.stderr)} 字符)"
        return f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}" if stderr else stdout
    except subprocess.TimeoutExpired:
        return "命令执行超时（>30s），已终止"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
