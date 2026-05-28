from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


class AuditLog(Document):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor_id: str
    actor_email: str
    action: Literal[
        "role_change", "user_deactivate", "user_activate",
        "policy_upload", "policy_delete",
        "claim_override", "login_failed", "login_success"
    ]
    target_type: Literal["user", "policy", "claim"]
    target_id: str
    details: dict = {}
    ip_address: str | None = None

    class Settings:
        name = "audit_logs"
        indexes = [
            IndexModel([("actor_id", ASCENDING)]),
            IndexModel([("action", ASCENDING)]),
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("target_type", ASCENDING)]),
        ]
