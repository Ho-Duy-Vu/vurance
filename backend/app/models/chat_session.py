from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import ASCENDING, DESCENDING, IndexModel


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatSession(Document):
    user_id: str
    messages: list[ChatMessage] = []
    message_count: int = 0
    context: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    async def add_message(self, message: ChatMessage):
        if len(self.messages) >= 50:
            self.messages = self.messages[-49:]
        self.messages.append(message)
        self.message_count += 1
        self.updated_at = datetime.utcnow()
        await self.save()

    class Settings:
        name = "chat_sessions"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("updated_at", DESCENDING)]),
        ]
