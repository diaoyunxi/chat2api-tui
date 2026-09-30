# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果"}
import subprocess

# Maximum output size in characters to prevent LLM context overflow and OOM (CWE-770).
# Commands producing output beyond this limit will be truncated with a notice.
MAX_OUTPUT_SIZE = 50_000

def _truncate(text: str, limit: int = MAX_OUTPUT_SIZE) -> str:
    """Truncate output if it exceeds the limit, appending a notice."""
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n\n... [output truncated: {len(text)} chars exceeded limit of {limit}]"

def exec_cmd(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.stderr:
            output = f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        else:
            output = result.stdout
        return _truncate(output)
    except Exception as e:
        return f"命令执行失败: {str(e)}"
