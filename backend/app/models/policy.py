from datetime import datetime

from beanie import Document
from pydantic import Field


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
        indexes = [("category", 1), ("is_active", 1)]
