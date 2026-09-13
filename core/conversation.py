"""对话管理：持久化保存/加载"""
import json
import os
from datetime import datetime

DATA_DIR = "data/conversations"

class Conversation:
    def __init__(self, title: str = "新对话"):
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.title = title
        self.messages: list[dict] = []
        self.system_prompt: str | None = None
        self.created_at = datetime.now().isoformat()

    def add_message(self, role: str, content: str, tool_calls: list = None):
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)

    def add_tool_result(self, tool_call_id: str, content: str):
        self.messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": content})

    def to_openai_format(self) -> list[dict]:
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": self.system_prompt})
        msgs.extend(self.messages)
        return msgs

    def save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        path = os.path.join(DATA_DIR, f"{self.id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "Conversation":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        conv = cls(data["title"])
        conv.id = data["id"]
        conv.messages = data["messages"]
        conv.system_prompt = data.get("system_prompt")
        conv.created_at = data.get("created_at", "")
        return conv

    @classmethod
    def list_conversations(cls) -> list[str]:
        if not os.path.exists(DATA_DIR):
            return []
        return [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
