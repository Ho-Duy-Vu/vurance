import re

from app.services.province_mapper import PROVINCE_REGION


def detect_province_from_text(address: str) -> str | None:
    """Extract province name from free-text address."""
    for province in PROVINCE_REGION:
        # Match province name ignoring case and common prefixes
        pattern = re.escape(province)
        if re.search(pattern, address, re.IGNORECASE):
            return province
    return None


def get_insurance_recommendations(province_name: str, risk_score: int, disaster_risks: list) -> list[dict]:
    region = PROVINCE_REGION.get(province_name, "north")
    recs = []

    # Always recommend basic property insurance
    recs.append({
        "insurance_type": "Bảo hiểm tài sản nhà ở",
        "priority_score": min(100, risk_score + 10),
        "reason": "Bảo vệ tài sản khỏi thiên tai và sự cố bất ngờ",
    })

    # Disaster-specific recommendations
    disaster_map = {
        "storm": ("Bảo hiểm thiên tai bão", "Khu vực thường xuyên chịu ảnh hưởng bão"),
        "flood": ("Bảo hiểm lũ lụt ngập lụt", "Nguy cơ lũ lụt cao trong mùa mưa"),
        "landslide": ("Bảo hiểm sạt lở đất", "Địa hình đồi núi có nguy cơ sạt lở"),
        "drought": ("Bảo hiểm nông nghiệp hạn hán", "Khu vực có nguy cơ hạn hán ảnh hưởng sản xuất"),
        "inundation": ("Bảo hiểm ngập úng đô thị", "Hệ thống thoát nước dễ bị quá tải"),
    }

    for d_risk in disaster_risks:
        d_type = d_risk.get("type") if isinstance(d_risk, dict) else getattr(d_risk, "type", None)
        d_score = d_risk.get("risk_score", 0) if isinstance(d_risk, dict) else getattr(d_risk, "risk_score", 0)
        if d_type in disaster_map and d_score >= 50:
            ins_type, reason = disaster_map[d_type]
            recs.append({
                "insurance_type": ins_type,
                "priority_score": d_score,
                "reason": reason,
            })

    # Region-specific
    if region == "central" and risk_score >= 70:
        recs.append({
            "insurance_type": "Bảo hiểm toàn diện miền Trung",
            "priority_score": risk_score,
            "reason": "Miền Trung chịu nhiều loại thiên tai nhất cả nước",
        })

    return sorted(recs, key=lambda x: x["priority_score"], reverse=True)
