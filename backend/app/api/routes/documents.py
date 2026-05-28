import hashlib
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile

from app.api.deps import get_current_user
from app.core.rate_limit import limiter
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentUploadResponse
from app.services.storage import ensure_bucket, get_presigned_url, upload_file

router = APIRouter(prefix="/documents", tags=["documents"])

_ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "application/pdf": "pdf",
    "image/jpeg": "jpeg",
    "image/jpg": "jpeg",
    "image/png": "png",
}

_ALLOWED_DOC_TYPES = [
    "cccd", "cmnd", "driver_license", "passport",
    "vehicle_registration", "insurance_policy", "other",
]

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", status_code=201, response_model=DocumentUploadResponse)
@limiter.limit("10/minute")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    if doc_type not in _ALLOWED_DOC_TYPES:
        raise HTTPException(400, f"Invalid doc_type. Allowed: {', '.join(_ALLOWED_DOC_TYPES)}")

    content_type = (file.content_type or "").lower()
    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(415, "Unsupported file type. Allowed: PDF, JPG, PNG")

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(413, "File exceeds 20MB limit")

    file_ext = _ALLOWED_CONTENT_TYPES[content_type]
    file_hash = hashlib.md5(file_bytes).hexdigest()
    file_key = f"{current_user.id}/{uuid.uuid4()}.{file_ext}"
    original_name = file.filename or f"upload.{file_ext}"

    await ensure_bucket()
    await upload_file(file_bytes, file_key, content_type)

    doc = Document(
        user_id=str(current_user.id),
        file_name=original_name,
        file_key=file_key,
        file_hash=file_hash,
        file_type=file_ext,
        file_size_kb=max(1, len(file_bytes) // 1024),
        doc_type=doc_type,
        processing_status="pending",
    )
    await doc.insert()

    presigned_url = get_presigned_url(file_key)

    return DocumentUploadResponse(
        document_id=str(doc.id),
        file_name=doc.file_name,
        doc_type=doc.doc_type,
        file_size_kb=doc.file_size_kb,
        presigned_url=presigned_url,
        processing_status=doc.processing_status,
        created_at=doc.created_at,
    )


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
) -> list[DocumentResponse]:
    docs = await Document.find(Document.user_id == str(current_user.id)).to_list()
    return [DocumentResponse.from_doc(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    doc = await Document.get(document_id)
    if not doc or doc.user_id != str(current_user.id):
        raise HTTPException(404, "Document not found")
    return DocumentResponse.from_doc(doc)


@router.get("/{document_id}/download-url")
async def get_download_url(
    document_id: str,
    current_user: User = Depends(get_current_user),
) -> dict:
    doc = await Document.get(document_id)
    if not doc or doc.user_id != str(current_user.id):
        raise HTTPException(404, "Document not found")
    return {"presigned_url": get_presigned_url(doc.file_key)}
