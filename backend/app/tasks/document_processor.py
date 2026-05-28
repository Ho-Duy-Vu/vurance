import asyncio
import logging

from celery import Celery

from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "claimflow",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.task_track_started = True


@celery_app.task(
    name="process_document",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def process_document(self, document_id: str, file_bytes_b64: str, doc_type: str):
    import base64

    async def _run():
        from motor.motor_asyncio import AsyncIOMotorClient
        from beanie import init_beanie
        from app.models.document import Document
        from app.models.user import User
        from app.models.claim import Claim
        from app.models.geo_risk import GeoRisk
        from app.models.chat_session import ChatSession
        from app.models.policy import Policy
        from app.models.audit_log import AuditLog
        from app.services.ai.ocr import ocr_service

        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await init_beanie(
            database=client[settings.MONGODB_DB_NAME],
            document_models=[User, Document, Claim, GeoRisk, ChatSession, Policy, AuditLog],
        )

        file_bytes = base64.b64decode(file_bytes_b64)
        result = await ocr_service.get_or_extract(file_bytes, doc_type, document_id)
        logger.info("OCR done for %s — confidence=%.2f", document_id, result.get("confidence", 0))
        return result

    return asyncio.run(_run())
