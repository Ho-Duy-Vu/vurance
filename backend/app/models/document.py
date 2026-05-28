from datetime import datetime
from typing import Literal

from beanie import Document
from pydantic import BaseModel, Field
from pymongo import IndexModel, ASCENDING


class ExtractedField(BaseModel):
    key: str
    value: str | None = None
    confidence: float = 0.0
    bbox: list[float] | None = None


class DocumentEmbed(BaseModel):
    id: str
    doc_type: str
    file_name: str
    created_at: datetime


class Document(Document):
    user_id: str
    file_name: str
    file_key: str
    file_hash: str
    file_type: Literal["pdf", "jpg", "jpeg", "png"]
    file_size_kb: int

    doc_type: Literal[
        "cccd", "cmnd", "driver_license", "passport",
        "vehicle_registration", "insurance_policy", "other"
    ]

    raw_text: str | None = None
    extracted_fields: list[ExtractedField] = []
    structured_data: dict = {}
    ocr_confidence: float | None = None
    needs_manual_review: bool = False
    low_confidence_fields: list[str] = []

    version: int = 1
    edit_history: list[dict] = []

    is_merged: bool = False
    merged_from: list[str] = []
    merged_data: dict = {}

    export_json: str | None = None
    export_markdown: str | None = None

    processing_status: Literal["pending", "processing", "done", "failed"] = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "documents"
        indexes = [
            IndexModel([("user_id", ASCENDING)]),
            IndexModel([("doc_type", ASCENDING)]),
            IndexModel([("processing_status", ASCENDING)]),
            IndexModel([("file_hash", ASCENDING)]),
        ]
