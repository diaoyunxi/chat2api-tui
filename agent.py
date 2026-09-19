# agent.py
"""智能体循环：必须调用 stop 工具才结束，否则强制继续"""
import json
from typing import Dict, List

from core import config
from core.conversation import Conversation
from core.llm_client import LLMClient
from core.tool_loader import ToolLoader


class Agent:
    def __init__(self, llm_client: LLMClient, tool_loader: ToolLoader):
        self.llm = llm_client
        self.tools = tool_loader
        self.max_iterations = config.get("max_iterations", 20)
        self.stop_tool_name = "stop"  # 标记任务完成的工具名

    def run(self, conversation: Conversation, model: str = None) -> str:
        """
        智能体主循环：只有调用 stop 工具才结束，否则强制继续
        """
        if model is None:
            model = config.get("default_model", "deepseek-v4-flash")

        messages = conversation.to_openai_format()
        tools_schema = self.tools.get_tools_schema()
        tools_with_stop = self._ensure_stop_tool(tools_schema)

        for iteration in range(self.max_iterations):
            response = self.llm.chat_completion(
                messages,
                model=model,
                tools=tools_with_stop if tools_with_stop else None
            )
            choice = response.choices[0]
            msg = choice.message

            # ----- 情况1：检测到工具调用 -----
            if choice.finish_reason == "tool_calls" and msg.tool_calls:
                # 将助手消息加入历史
                if hasattr(msg, 'model_dump'):
                    conversation.messages.append(msg.model_dump())
                else:
                    conversation.messages.append(msg.to_dict())

                # 执行每个工具
                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    
                    # 如果是 stop 工具 → 任务完成，结束循环
                    if tool_name == self.stop_tool_name:
                        args = json.loads(tc.function.arguments)
                        final_reason = args.get("reason", "任务已完成")
                        # 将 stop 工具结果也加入历史（便于记录）
                        conversation.add_tool_result(tc.id, f"任务完成: {final_reason}")
                        return f"✅ 任务已按计划完成: {final_reason}"

                    # 执行其他工具
                    args = json.loads(tc.function.arguments)
                    print(f"🔧 调用工具: {tool_name}({args})")
                    result = self.tools.execute(tool_name, args)
                    conversation.add_tool_result(tc.id, result)

                # 更新 messages 继续循环
                messages = conversation.to_openai_format()
                continue

            # ----- 情况2：没有工具调用（finish_reason == "stop"）-----
            # 模型输出了普通文本，但没有调用任何工具，包括 stop
            final_text = msg.content or ""
            if not conversation.messages or conversation.messages[-1].get("role") != "assistant":
                conversation.add_message("assistant", final_text)

            # 强制要求调用 stop 或继续执行
            conversation.add_message(
                "user",
                "请确认任务是否完成。如果完成，请立即调用 stop 工具并附上完成原因；如果未完成，请继续执行剩余的工具调用，不要只输出文本计划。"
            )
            messages = conversation.to_openai_format()
            print("⏳ 未检测到 stop 工具调用，强制继续...")
            continue

        # 达到最大循环次数
        return f"⚠️ 达到最大循环次数 ({self.max_iterations})，任务可能未完全完成。请手动检查。"

    def _ensure_stop_tool(self, tools_schema: List[Dict]) -> List[Dict]:
        """确保 tools 列表中包含 stop 工具"""
        if not tools_schema:
            # 如果没有任何工具，只返回 stop 工具
            return [self._create_stop_tool()]

        # 如果已经包含 stop 工具，直接返回
        for tool in tools_schema:
            if tool.get("function", {}).get("name") == self.stop_tool_name:
                return tools_schema

        # 否则添加 stop 工具
        return tools_schema + [self._create_stop_tool()]

    def _create_stop_tool(self) -> Dict:
        """创建 stop 工具的定义"""
        return {
            "type": "function",
            "function": {
                "name": "stop",
                "description": "当任务已经完全完成时调用此工具，表示不再需要继续执行任何操作",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "任务完成的原因或总结"
                        }
                    },
                    "required": ["reason"]
                }
            }
        }

    def run_with_image(self, conversation: Conversation, text: str, image_path: str, model: str = None) -> str:
        """处理图片消息的多模态版本"""
        if model is None:
            model = config.get("default_model", "deepseek-v4-flash")
        msg = LLMClient.build_multimodal_message(text, image_path=image_path)
        conversation.messages.append(msg)
        return self.run(conversation, model)