"""Agent Memory — conversation history and context management."""
from typing import TypedDict


class Message(TypedDict):
    role: str
    content: str


class ConversationMemory:
    """Sliding-window conversation memory."""

    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.messages: list[Message] = []
        self.context: dict = {}

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_messages(self) -> list[Message]:
        return list(self.messages)

    def get_context(self, key: str, default=None):
        return self.context.get(key, default)

    def set_context(self, key: str, value):
        self.context[key] = value

    def clear(self):
        self.messages.clear()
        self.context.clear()

    def to_dict(self) -> dict:
        return {
            "messages": self.messages,
            "context": self.context,
        }

    def from_dict(self, data: dict):
        self.messages = data.get("messages", [])
        self.context = data.get("context", {})
