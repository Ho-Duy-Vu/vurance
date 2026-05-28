import logging
from datetime import datetime

from app.models.document import Document

logger = logging.getLogger(__name__)


def _merge_structured_data(docs: list[dict]) -> tuple[dict, dict]:
    """Merge structured_data from multiple documents; detect field conflicts."""
    merged: dict = {}
    conflicts: dict = {}
    sources: dict = {}

    for doc_data in docs:
        doc_id = doc_data["id"]
        data = doc_data.get("structured_data", {})

        for key, val in data.items():
            if key == "overall_confidence":
                continue

            normalized = val.get("value") if isinstance(val, dict) else val

            if key not in merged:
                merged[key] = normalized
                sources[key] = [doc_id]
            elif merged[key] is None and normalized is not None:
                merged[key] = normalized
                sources[key].append(doc_id)
            elif normalized is not None and normalized != merged[key]:
                if key not in conflicts:
                    conflicts[key] = {
                        "values": [merged[key]],
                        "source_docs": sources.get(key, []),
                    }
                if normalized not in conflicts[key]["values"]:
                    conflicts[key]["values"].append(normalized)
                    conflicts[key]["source_docs"].append(doc_id)

    return merged, conflicts


class MergerService:
    async def merge(self, doc_ids: list[str], user_id: str) -> dict:
        if len(doc_ids) < 2:
            raise ValueError("Need at least 2 documents to merge")

        docs = []
        for doc_id in doc_ids:
            doc = await Document.get(doc_id)
            if not doc or doc.user_id != user_id:
                raise ValueError(f"Document {doc_id} not found or access denied")
            docs.append(doc)

        doc_data_list = [
            {"id": str(d.id), "doc_type": d.doc_type, "structured_data": d.structured_data}
            for d in docs
        ]

        merged_data, conflicts = _merge_structured_data(doc_data_list)

        merged_doc = Document(
            user_id=user_id,
            file_name=f"merged_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
            file_key="",
            file_hash="",
            file_type="pdf",
            file_size_kb=0,
            doc_type=docs[0].doc_type,
            is_merged=True,
            merged_from=[str(d.id) for d in docs],
            merged_data=merged_data,
            structured_data=merged_data,
            processing_status="done",
        )
        await merged_doc.insert()

        logger.info("Merged %d docs → %s | conflicts: %d", len(docs), merged_doc.id, len(conflicts))

        return {
            "merged_document_id": str(merged_doc.id),
            "merged_data": merged_data,
            "conflicts": conflicts,
            "source_doc_ids": [str(d.id) for d in docs],
        }


merger_service = MergerService()
