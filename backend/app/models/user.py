from datetime import datetime
from typing import Literal

from beanie import Document, Indexed
from pydantic import EmailStr, Field
from pymongo import IndexModel, ASCENDING


class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: str | None = None
    role: Literal["user", "reviewer", "admin"] = "user"
    province: str | None = None
    region: Literal["north", "central", "south"] | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [
            IndexModel([("role", ASCENDING)]),
            IndexModel([("province", ASCENDING)]),
            IndexModel([("is_active", ASCENDING)]),
        ]
