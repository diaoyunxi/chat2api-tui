"""对话管理：持久化保存/加载"""
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Optional

DATA_DIR = "data/conversations"

class Conversation:
    def __init__(self, title: str = "新对话"):
        self.id = self._generate_unique_id()
        self.title = title
        self.messages: List[Dict] = []
        self.system_prompt: Optional[str] = None
        self.created_at = datetime.now().isoformat()

    @staticmethod
    def _generate_unique_id() -> str:
        """生成唯一对话 ID，避免同一秒内创建多个对话时 ID 碰撞。

        使用时间戳精确到微秒 + 碰撞检测：若目标文件已存在，追加递增后缀。
        """
        base = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        candidate = base
        suffix = 1
        while os.path.exists(os.path.join(DATA_DIR, f"{candidate}.json")):
            candidate = f"{base}_{suffix}"
            suffix += 1
        return candidate

    def add_message(self, role: str, content: str, tool_calls: List = None):
        msg = {"role": role, "content": content}
        if tool_calls:
            msg["tool_calls"] = tool_calls
        self.messages.append(msg)

    def add_tool_result(self, tool_call_id: str, content: str):
        self.messages.append({"role": "tool", "tool_call_id": tool_call_id, "content": content})

    def to_openai_format(self) -> List[Dict]:
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
    def list_conversations(cls) -> List[str]:
        if not os.path.exists(DATA_DIR):
            return []
        return [f for f in os.listdir(DATA_DIR) if f.endswith(".json")]
