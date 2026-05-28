from datetime import datetime

from beanie import Document
from pydantic import Field
from pymongo import IndexModel, ASCENDING


class Policy(Document):
    title: str
    content: str
    category: str
    coverage_types: list[str] = []
    version: str
    is_active: bool = True
    chunk_count: int = 0
    last_ingested: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "policies"
        indexes = [
            IndexModel([("category", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
        ]
