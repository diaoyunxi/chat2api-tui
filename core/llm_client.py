# core/llm_client.py
import base64
import os
from openai import OpenAI
from typing import List, Dict, Any, Optional
from core import config  # 新增

class LLMClient:
    def __init__(self, base_url: str = None, api_key: str = None,
                 timeout: float = 60.0, max_retries: int = 2):
        # 优先使用传入参数，否则从配置文件读取
        self.base_url = base_url or config.get("base_url")
        self.api_key = api_key or config.get("api_key")
        if not self.api_key:
            raise ValueError("API Key 未配置，请在 config.yml 中设置 api_key")
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

    def chat_completion(self, messages: List[Dict], model: str = None,
                         tools: Optional[List[Dict]] = None, stream: bool = False):
        if model is None:
            model = config.get("default_model")
        kwargs: Dict[str, Any] = {"model": model, "messages": messages, "stream": stream}
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        return self.client.chat.completions.create(**kwargs)

    # build_multimodal_message 保持不变
    @staticmethod
    def build_multimodal_message(text: str, image_path: str = None, image_url: str = None) -> Dict:
        content = [{"type": "text", "text": text}]
        if image_path:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
        elif image_url:
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        return {"role": "user", "content": content}
