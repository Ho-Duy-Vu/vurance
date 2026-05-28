from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import Field

from app.models.document import DocumentEmbed


class Claim(Document):
    user_id: str
    status: Literal["pending", "processing", "approved", "rejected", "manual_review"] = "pending"
    claim_type: Literal["medical", "dental", "hospitalization", "medication", "disaster"]

    amount_claimed: float
    amount_approved: float | None = None

    documents: list[DocumentEmbed] = []

    ai_decision: str | None = None
    ai_reasoning: str | None = None
    ai_fraud_score: int | None = None
    ai_fraud_flags: list[str] = []
    ai_parsed_data: dict | None = None

    province: str | None = None
    disaster_type: str | None = None

    reviewer_id: str | None = None
    reviewer_note: str | None = None
    reviewed_at: datetime | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None

    class Settings:
        name = "claims"
        indexes = [
            ("user_id", 1),
            ("status", 1),
            ("province", 1),
            ("created_at", -1),
        ]
