import base64
import hashlib
import json
import logging
import re

import google.generativeai as genai

from app.core.config import settings
from app.models.document import Document

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7

_OCR_PROMPTS: dict[str, str] = {
    "cccd": """Extract all text from this Vietnamese CCCD (National ID card) image.
Return ONLY valid JSON with this structure:
{
  "id_number": {"value": "...", "confidence": 0.0},
  "full_name": {"value": "...", "confidence": 0.0},
  "date_of_birth": {"value": "...", "confidence": 0.0},
  "gender": {"value": "...", "confidence": 0.0},
  "nationality": {"value": "...", "confidence": 0.0},
  "place_of_origin": {"value": "...", "confidence": 0.0},
  "place_of_residence": {"value": "...", "confidence": 0.0},
  "expiry_date": {"value": "...", "confidence": 0.0},
  "overall_confidence": 0.0
}
Confidence scores must be 0.0–1.0. Use null for missing fields.""",

    "cmnd": """Extract all text from this Vietnamese CMND (old National ID) image.
Return ONLY valid JSON with the same structure as CCCD but adapted for CMND fields.
Include overall_confidence as average of field confidences.""",

    "driver_license": """Extract all text from this Vietnamese Driver's License image.
Return ONLY valid JSON:
{
  "license_number": {"value": "...", "confidence": 0.0},
  "full_name": {"value": "...", "confidence": 0.0},
  "date_of_birth": {"value": "...", "confidence": 0.0},
  "address": {"value": "...", "confidence": 0.0},
  "license_class": {"value": "...", "confidence": 0.0},
  "issue_date": {"value": "...", "confidence": 0.0},
  "expiry_date": {"value": "...", "confidence": 0.0},
  "overall_confidence": 0.0
}""",

    "passport": """Extract all text from this passport image (MRZ and biographical data).
Return ONLY valid JSON:
{
  "passport_number": {"value": "...", "confidence": 0.0},
  "full_name": {"value": "...", "confidence": 0.0},
  "nationality": {"value": "...", "confidence": 0.0},
  "date_of_birth": {"value": "...", "confidence": 0.0},
  "gender": {"value": "...", "confidence": 0.0},
  "place_of_birth": {"value": "...", "confidence": 0.0},
  "issue_date": {"value": "...", "confidence": 0.0},
  "expiry_date": {"value": "...", "confidence": 0.0},
  "overall_confidence": 0.0
}""",

    "insurance_policy": """Extract key information from this Vietnamese insurance policy document.
Return ONLY valid JSON:
{
  "policy_number": {"value": "...", "confidence": 0.0},
  "insured_name": {"value": "...", "confidence": 0.0},
  "coverage_types": {"value": "...", "confidence": 0.0},
  "coverage_amount": {"value": "...", "confidence": 0.0},
  "premium": {"value": "...", "confidence": 0.0},
  "start_date": {"value": "...", "confidence": 0.0},
  "end_date": {"value": "...", "confidence": 0.0},
  "insurer": {"value": "...", "confidence": 0.0},
  "overall_confidence": 0.0
}""",

    "vehicle_registration": """Extract all text from this Vietnamese vehicle registration document.
Return ONLY valid JSON:
{
  "plate_number": {"value": "...", "confidence": 0.0},
  "owner_name": {"value": "...", "confidence": 0.0},
  "owner_address": {"value": "...", "confidence": 0.0},
  "vehicle_type": {"value": "...", "confidence": 0.0},
  "brand": {"value": "...", "confidence": 0.0},
  "color": {"value": "...", "confidence": 0.0},
  "engine_number": {"value": "...", "confidence": 0.0},
  "chassis_number": {"value": "...", "confidence": 0.0},
  "registration_date": {"value": "...", "confidence": 0.0},
  "overall_confidence": 0.0
}""",

    "other": """Extract all readable text from this document image.
Return ONLY valid JSON:
{
  "raw_text": {"value": "...", "confidence": 0.0},
  "overall_confidence": 0.0
}""",
}

_ENHANCED_SUFFIX = """
IMPORTANT: This image may be low quality. Use maximum effort to extract any visible text.
Increase confidence only for clearly readable fields. Set confidence=0.0 for unreadable fields."""


def _build_prompt(doc_type: str, enhanced: bool = False) -> str:
    base = _OCR_PROMPTS.get(doc_type, _OCR_PROMPTS["other"])
    return base + _ENHANCED_SUFFIX if enhanced else base


def _parse_gemini_response(text: str) -> dict:
    text = text.strip()
    # Extract JSON from markdown code blocks if present
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        text = match.group(1)
    return json.loads(text)


class OCRService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model = genai.GenerativeModel("gemini-1.5-flash")

    async def get_or_extract(self, file_bytes: bytes, doc_type: str, document_id: str) -> dict:
        file_hash = hashlib.md5(file_bytes).hexdigest()

        cached = await Document.find_one(
            Document.file_hash == file_hash,
            Document.processing_status == "done",
        )
        if cached and cached.structured_data:
            logger.info("OCR cache hit for hash %s", file_hash)
            return {
                "data": cached.structured_data,
                "confidence": cached.ocr_confidence,
                "cached": True,
                "needs_manual_review": cached.needs_manual_review,
                "low_confidence_fields": cached.low_confidence_fields,
            }

        return await self._extract_with_retry(file_bytes, doc_type, document_id, file_hash)

    async def _extract_with_retry(
        self, file_bytes: bytes, doc_type: str, document_id: str, file_hash: str
    ) -> dict:
        doc = await Document.get(document_id)
        if doc:
            doc.processing_status = "processing"
            await doc.save()

        result = await self._call_gemini(file_bytes, doc_type, enhanced=False)
        confidence = result.get("overall_confidence", 0.0)

        if confidence < CONFIDENCE_THRESHOLD:
            logger.warning("[%s] Low confidence %.2f, retrying with enhanced prompt", document_id, confidence)
            retry = await self._call_gemini(file_bytes, doc_type, enhanced=True)
            if retry.get("overall_confidence", 0.0) >= confidence:
                result = retry
                confidence = result.get("overall_confidence", 0.0)

        low_conf_fields = [
            k for k, v in result.items()
            if isinstance(v, dict) and v.get("confidence", 1.0) < CONFIDENCE_THRESHOLD
        ]

        needs_review = confidence < CONFIDENCE_THRESHOLD

        if doc:
            doc.structured_data = result
            doc.ocr_confidence = confidence
            doc.needs_manual_review = needs_review
            doc.low_confidence_fields = low_conf_fields
            doc.processing_status = "done" if not needs_review else "done"
            doc.file_hash = file_hash
            await doc.save()

        return {
            "data": result,
            "confidence": confidence,
            "cached": False,
            "needs_manual_review": needs_review,
            "low_confidence_fields": low_conf_fields,
        }

    async def _call_gemini(self, file_bytes: bytes, doc_type: str, enhanced: bool) -> dict:
        prompt = _build_prompt(doc_type, enhanced)
        image_data = base64.b64encode(file_bytes).decode()

        # Detect MIME type from first bytes
        if file_bytes[:4] == b"%PDF":
            mime = "application/pdf"
        elif file_bytes[:3] == b"\xff\xd8\xff":
            mime = "image/jpeg"
        else:
            mime = "image/png"

        image_part = {"mime_type": mime, "data": image_data}

        try:
            response = self._model.generate_content([image_part, prompt])
            parsed = _parse_gemini_response(response.text)
            return parsed
        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Gemini response parse error: %s", e)
            return {"overall_confidence": 0.0, "parse_error": str(e)}
        except Exception as e:
            logger.error("Gemini API error: %s", e)
            raise


ocr_service = OCRService()
