"""
Seed script — chạy một lần để khởi tạo dữ liệu mẫu:
  - 1 admin, 1 reviewer, 3 users
  - 63 province risk records

Usage:
    cd backend
    python scripts/seed.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

from app.models.audit_log import AuditLog
from app.models.chat_session import ChatSession
from app.models.claim import Claim
from app.models.document import Document
from app.models.geo_risk import DisasterRisk, GeoRisk, InsuranceRecommendation
from app.models.policy import Policy
from app.models.user import User
from app.core.config import settings
from app.core.security import hash_password

# ── Province data ─────────────────────────────────────────────────────────────

HIGH_RISK_PROVINCES = {
    "Quảng Bình", "Hà Tĩnh", "Nghệ An", "Quảng Nam",
    "Thừa Thiên Huế", "Quảng Ngãi", "Bình Định", "Quảng Trị",
}

MOUNTAINOUS_NORTH = {
    "Sơn La", "Điện Biên", "Lai Châu", "Hà Giang",
    "Lào Cai", "Cao Bằng", "Bắc Kạn",
}

FLOOD_SOUTH = {
    "An Giang", "Đồng Tháp", "Long An",
    "Tiền Giang", "Kiên Giang", "Cà Mau",
}

PROVINCES = [
    # (name, code, region)
    # ── Bắc Bộ (25) ───────────────────────────────────────────────────────────
    ("Hà Nội",          "HN",   "north"),
    ("Hải Phòng",       "HP",   "north"),
    ("Quảng Ninh",      "QNI",  "north"),
    ("Hải Dương",       "HD",   "north"),
    ("Hưng Yên",        "HY",   "north"),
    ("Thái Bình",       "THBI", "north"),
    ("Nam Định",        "NDIN", "north"),
    ("Ninh Bình",       "NBI",  "north"),
    ("Hà Nam",          "HNA",  "north"),
    ("Bắc Ninh",        "BNI",  "north"),
    ("Vĩnh Phúc",       "VP",   "north"),
    ("Phú Thọ",         "PT",   "north"),
    ("Thái Nguyên",     "TNGU", "north"),
    ("Bắc Giang",       "BG",   "north"),
    ("Bắc Kạn",         "BK",   "north"),
    ("Cao Bằng",        "CB",   "north"),
    ("Lạng Sơn",        "LSN",  "north"),
    ("Lào Cai",         "LC",   "north"),
    ("Yên Bái",         "YB",   "north"),
    ("Hà Giang",        "HGI",  "north"),
    ("Tuyên Quang",     "TQ",   "north"),
    ("Sơn La",          "SLA",  "north"),
    ("Điện Biên",       "DB",   "north"),
    ("Lai Châu",        "LAC",  "north"),
    ("Hòa Bình",        "HOB",  "north"),
    # ── Trung Bộ (19) ─────────────────────────────────────────────────────────
    ("Thanh Hóa",       "TH",   "central"),
    ("Nghệ An",         "NA",   "central"),
    ("Hà Tĩnh",         "HT",   "central"),
    ("Quảng Bình",      "QB",   "central"),
    ("Quảng Trị",       "QTR",  "central"),
    ("Thừa Thiên Huế",  "TTH",  "central"),
    ("Đà Nẵng",         "DN",   "central"),
    ("Quảng Nam",       "QNA",  "central"),
    ("Quảng Ngãi",      "QNG",  "central"),
    ("Bình Định",       "BDIN", "central"),
    ("Phú Yên",         "PY",   "central"),
    ("Khánh Hòa",       "KH",   "central"),
    ("Ninh Thuận",      "NTHU", "central"),
    ("Bình Thuận",      "BTH",  "central"),
    ("Kon Tum",         "KT",   "central"),
    ("Gia Lai",         "GL",   "central"),
    ("Đắk Lắk",         "DL",   "central"),
    ("Đắk Nông",        "DAN",  "central"),
    ("Lâm Đồng",        "LD",   "central"),
    # ── Nam Bộ (19) ───────────────────────────────────────────────────────────
    ("TP. Hồ Chí Minh", "HCM",  "south"),
    ("Bình Dương",      "BDG",  "south"),
    ("Đồng Nai",        "DNI",  "south"),
    ("Bà Rịa-Vũng Tàu","BRVT", "south"),
    ("Long An",         "LA",   "south"),
    ("Tiền Giang",      "TIG",  "south"),
    ("Bến Tre",         "BTE",  "south"),
    ("Trà Vinh",        "TV",   "south"),
    ("Vĩnh Long",       "VL",   "south"),
    ("Đồng Tháp",       "DTP",  "south"),
    ("An Giang",        "AG",   "south"),
    ("Kiên Giang",      "KIG",  "south"),
    ("Cần Thơ",         "CT",   "south"),
    ("Hậu Giang",       "HGG",  "south"),
    ("Sóc Trăng",       "ST",   "south"),
    ("Bạc Liêu",        "BL",   "south"),
    ("Cà Mau",          "CM",   "south"),
    ("Tây Ninh",        "TN",   "south"),
    ("Bình Phước",      "BP",   "south"),
]

BASE_SCORES = {"central": 65, "north": 42, "south": 38}


def _build_province(name: str, code: str, region: str) -> dict:
    is_high_risk = name in HIGH_RISK_PROVINCES
    score = BASE_SCORES[region]
    risk_factors: list[str] = []
    disaster_risks: list[DisasterRisk] = []
    recommendations: list[InsuranceRecommendation] = []

    if is_high_risk:
        score += 25
        risk_factors += ["typhoon_path", "flood_prone"]
        if name in {"Quảng Bình", "Hà Tĩnh", "Quảng Nam", "Thừa Thiên Huế", "Quảng Trị"}:
            risk_factors.append("mountainous")
            disaster_risks = [
                DisasterRisk(type="storm",     risk_score=95, frequency="high",   historical_events=47),
                DisasterRisk(type="flood",     risk_score=90, frequency="high",   historical_events=38),
                DisasterRisk(type="landslide", risk_score=72, frequency="medium", historical_events=14),
            ]
        else:
            disaster_risks = [
                DisasterRisk(type="storm", risk_score=82, frequency="high", historical_events=35),
                DisasterRisk(type="flood", risk_score=78, frequency="high", historical_events=29),
            ]
        recommendations = [
            InsuranceRecommendation(
                insurance_type="Bảo hiểm bão lũ",
                priority_score=95,
                reason=f"{name} nằm trên đường đi của bão miền Trung",
            ),
            InsuranceRecommendation(
                insurance_type="Bảo hiểm nhà ở",
                priority_score=88,
                reason="Nguy cơ ngập lụt và sạt lở cao",
            ),
            InsuranceRecommendation(
                insurance_type="Bảo hiểm nông nghiệp",
                priority_score=80,
                reason="Thiệt hại mùa vụ thường xuyên do thiên tai",
            ),
        ]

    elif name in MOUNTAINOUS_NORTH:
        score += 12
        risk_factors += ["mountainous", "landslide_prone"]
        disaster_risks = [
            DisasterRisk(type="landslide", risk_score=75, frequency="medium", historical_events=18),
            DisasterRisk(type="flood",     risk_score=55, frequency="medium", historical_events=12),
        ]
        recommendations = [
            InsuranceRecommendation(
                insurance_type="Bảo hiểm sạt lở đất",
                priority_score=78,
                reason="Địa hình núi cao, nguy cơ sạt lở lớn",
            ),
            InsuranceRecommendation(
                insurance_type="Bảo hiểm nhà ở",
                priority_score=70,
                reason="Bảo vệ nhà trước thiên tai miền núi",
            ),
        ]

    elif name in FLOOD_SOUTH:
        score += 15
        risk_factors += ["flood_prone", "delta_area"]
        disaster_risks = [
            DisasterRisk(type="inundation", risk_score=80, frequency="high",   historical_events=30),
            DisasterRisk(type="flood",      risk_score=75, frequency="high",   historical_events=25),
        ]
        recommendations = [
            InsuranceRecommendation(
                insurance_type="Bảo hiểm ngập nước",
                priority_score=85,
                reason="Đồng bằng sông Cửu Long ngập lụt theo mùa",
            ),
            InsuranceRecommendation(
                insurance_type="Bảo hiểm nông nghiệp",
                priority_score=82,
                reason="Vùng nông nghiệp trọng điểm, rủi ro mùa vụ cao",
            ),
        ]

    else:
        if region == "central":
            disaster_risks = [
                DisasterRisk(type="storm", risk_score=60, frequency="medium", historical_events=20),
                DisasterRisk(type="flood", risk_score=55, frequency="medium", historical_events=15),
            ]
        elif region == "north":
            disaster_risks = [
                DisasterRisk(type="flood",   risk_score=40, frequency="low", historical_events=8),
                DisasterRisk(type="drought", risk_score=30, frequency="low", historical_events=5),
            ]
        else:
            disaster_risks = [
                DisasterRisk(type="flood",   risk_score=45, frequency="medium", historical_events=10),
                DisasterRisk(type="drought", risk_score=35, frequency="low",    historical_events=6),
            ]
        recommendations = [
            InsuranceRecommendation(
                insurance_type="Bảo hiểm nhân thọ",
                priority_score=65,
                reason="Bảo vệ tài chính gia đình",
            ),
            InsuranceRecommendation(
                insurance_type="Bảo hiểm sức khỏe",
                priority_score=70,
                reason="Chi phí y tế ngày càng tăng",
            ),
        ]

    is_flagged = is_high_risk or name in MOUNTAINOUS_NORTH or name in FLOOD_SOUTH
    return dict(
        province_name=name,
        province_code=code,
        region=region,
        overall_risk_score=min(100, score),
        disaster_risks=disaster_risks,
        recommendations=recommendations,
        is_high_risk=is_flagged,
        risk_factors=risk_factors,
    )


# ── Seed functions ─────────────────────────────────────────────────────────────

async def seed_users():
    print("Seeding users...")
    users_data = [
        dict(email="admin@claimflow.vn",    hashed_password=hash_password("Admin@123"),
             full_name="Admin ClaimFlow",   role="admin",    province="Hà Nội",          region="north"),
        dict(email="reviewer@claimflow.vn", hashed_password=hash_password("Reviewer@123"),
             full_name="Trần Thị Bình",     role="reviewer", province="TP. Hồ Chí Minh", region="south"),
        dict(email="user1@example.com",     hashed_password=hash_password("User1@123"),
             full_name="Nguyễn Văn An",     role="user",     province="Quảng Bình",       region="central"),
        dict(email="user2@example.com",     hashed_password=hash_password("User2@123"),
             full_name="Lê Thị Cẩm",        role="user",     province="Hà Nội",           region="north"),
        dict(email="user3@example.com",     hashed_password=hash_password("User3@123"),
             full_name="Phạm Minh Đức",     role="user",     province="TP. Hồ Chí Minh",  region="south"),
    ]
    created = 0
    for u in users_data:
        existing = await User.find_one(User.email == u["email"])
        if not existing:
            await User(**u).insert()
            created += 1
    skipped = len(users_data) - created
    print(f"  ✓ {created} users created ({skipped} already exist)")


async def seed_geo_risks():
    print(f"Seeding geo risks ({len(PROVINCES)} provinces)...")
    created = 0
    for name, code, region in PROVINCES:
        existing = await GeoRisk.find_one(GeoRisk.province_name == name)
        if not existing:
            data = _build_province(name, code, region)
            await GeoRisk(**data).insert()
            created += 1
    skipped = len(PROVINCES) - created
    print(f"  ✓ {created} provinces created ({skipped} already exist)")


async def main():
    print("=" * 50)
    print("ClaimFlow Seed Script")
    print("=" * 50)
    print(f"Connecting to {settings.MONGODB_URL}...")

    client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_beanie(
        database=client[settings.MONGODB_DB_NAME],
        document_models=[User, Document, Claim, GeoRisk, ChatSession, Policy, AuditLog],
    )
    print(f"✓ Connected to [{settings.MONGODB_DB_NAME}]\n")

    await seed_users()
    await seed_geo_risks()

    total_users     = await User.count()
    total_provinces = await GeoRisk.count()
    high_risk       = await GeoRisk.find(GeoRisk.is_high_risk == True).count()

    print("\n" + "=" * 50)
    print(f"  Users:          {total_users}")
    print(f"  Provinces:      {total_provinces}")
    print(f"  High-risk:      {high_risk}")
    print("=" * 50)
    print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
