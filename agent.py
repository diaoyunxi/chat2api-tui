# agent.py
"""智能体循环：自动检测工具调用，执行后带回结果，支持多轮"""
import json
from typing import List, Dict, Any
from core.llm_client import LLMClient
from core.tool_loader import ToolLoader
from core.conversation import Conversation
from core import config

class Agent:
    def __init__(self, llm_client, tool_loader):
        self.llm = llm_client
        self.tools = tool_loader
        self.max_iterations = config.get("max_iterations", 10)
    def run(self, conversation: Conversation, model: str = "deepseek-v4-flash") -> str:
        """执行智能体循环，返回最终文本回复，可指定模型"""
        messages = conversation.to_openai_format()
        tools_schema = self.tools.get_tools_schema()

        for _ in range(self.max_iterations):
            response = self.llm.chat_completion(
                messages, 
                model=model, 
                tools=tools_schema if tools_schema else None
            )
            choice = response.choices[0]
            msg = choice.message

            # 检测是否有工具调用
            if choice.finish_reason == "tool_calls" and msg.tool_calls:
                # 将助手消息（含 tool_calls）加入历史
                if hasattr(msg, 'model_dump'):
                    conversation.messages.append(msg.model_dump())
                else:
                    conversation.messages.append(msg.to_dict())

                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    args = json.loads(tc.function.arguments)
                    print(f"🔧 调用工具: {tool_name}({args})")
                    result = self.tools.execute(tool_name, args)
                    # 将工具结果加入历史
                    conversation.add_tool_result(tc.id, result)

                # 更新 messages 列表继续循环
                messages = conversation.to_openai_format()
                continue

            # 没有工具调用，返回最终回复
            final_text = msg.content or ""
            if not conversation.messages or conversation.messages[-1].get("role") != "assistant":
                conversation.add_message("assistant", final_text)
            return final_text

        return "⚠️ 达到最大循环次数，可能陷入死循环"

    def run_with_image(self, conversation: Conversation, text: str, image_path: str, model: str = "deepseek-v4-flash") -> str:
        """处理图片消息的多模态版本"""
        msg = LLMClient.build_multimodal_message(text, image_path=image_path)
        conversation.messages.append(msg)
        return self.run(conversation, model)
