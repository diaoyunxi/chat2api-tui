# tool: {"name": "stop", "description": "当任务已经完全完成时调用此工具，表示不再需要继续执行任何操作"}

def stop(reason: str = "任务已完成") -> str:
    """
    标记任务完成。
    
    Args:
        reason: 完成原因，默认"任务已完成"
    
    Returns:
        固定确认消息
    """
    return f"✅ 任务已标记为完成: {reason}"