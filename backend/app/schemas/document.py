from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    file_name: str
    doc_type: str
    file_size_kb: int
    presigned_url: str
    processing_status: str
    created_at: datetime


class DocumentResponse(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    doc_type: str
    file_size_kb: int
    processing_status: str
    ocr_confidence: float | None
    needs_manual_review: bool
    is_merged: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_doc(cls, doc) -> "DocumentResponse":  # noqa: ANN001
        return cls(
            document_id=str(doc.id),
            file_name=doc.file_name,
            file_type=doc.file_type,
            doc_type=doc.doc_type,
            file_size_kb=doc.file_size_kb,
            processing_status=doc.processing_status,
            ocr_confidence=doc.ocr_confidence,
            needs_manual_review=doc.needs_manual_review,
            is_merged=doc.is_merged,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )


class DocumentOCRResponse(BaseModel):
    document_id: str
    processing_status: str
    structured_data: dict[str, Any]
    ocr_confidence: float | None
    needs_manual_review: bool
    low_confidence_fields: list[str]
