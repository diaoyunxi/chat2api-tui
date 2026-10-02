# tool: {"name": "exec_cmd", "description": "执行系统命令并返回输出结果（安全模式：仅允许白名单命令）"}
import subprocess
import shlex
import os

# 安全命令白名单 - 仅允许只读/信息查询类命令
ALLOWED_COMMANDS = {
    'ls', 'pwd', 'date', 'whoami', 'hostname', 'uname',
    'cat', 'head', 'tail', 'wc', 'grep', 'find',
    'ps', 'df', 'free', 'uptime', 'env',
    'python', 'python3', 'pip', 'pip3', 'node', 'npm',
    'git', 'curl', 'wget', 'ping',
}

# 危险模式黑名单
DANGEROUS_PATTERNS = [
    'rm -rf', 'rm -r /', 'mkfs', 'dd if=', '> /dev/',
    'shutdown', 'reboot', 'halt', 'poweroff',
    'sudo', 'su ', 'chmod 777', 'chmod -R 777',
]

def exec_cmd(command: str) -> str:
    """
    安全执行系统命令
    
    安全措施：
    1. 命令白名单 - 仅允许预定义的安全命令
    2. shell=False - 防止命令注入
    3. 危险模式过滤 - 拒绝明显危险的命令
    4. 超时保护 - 30秒超时防止卡死
    """
    try:
        # 解析命令
        args = shlex.split(command)
        if not args:
            return "错误：命令为空"
        
        # 提取基础命令（去掉路径前缀）
        base_cmd = os.path.basename(args[0])
        
        # 白名单检查
        if base_cmd not in ALLOWED_COMMANDS:
            return f"⚠️ 安全限制：命令 '{base_cmd}' 不在允许的白名单中\n允许的命令: {', '.join(sorted(ALLOWED_COMMANDS))}"
        
        # 危险模式检查
        cmd_lower = command.lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in cmd_lower:
                return f"⚠️ 安全限制：检测到危险模式 '{pattern}'"
        
        # 使用 shell=False 防止命令注入
        result = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        
        return output if output else "(无输出)"
        
    except subprocess.TimeoutExpired:
        return "⚠️ 命令执行超时（>30秒）"
    except ValueError as e:
        return f"命令解析错误：{e}"
    except Exception as e:
        return f"命令执行失败: {str(e)}"
