"""
scripts/seed.py — ClaimFlow Test Data Generator
================================================
Tạo toàn bộ dữ liệu test cho ClaimFlow:
  - Users (1 admin, 2 reviewers, 10 users)
  - GeoRisk data (64 tỉnh/thành Việt Nam)
  - Policy documents (medical + disaster)
  - Claims với đủ statuses
  - Chat sessions
  - Audit logs mẫu

Chạy: python scripts/seed.py
Yêu cầu: MongoDB đang chạy tại localhost:27017
"""

import asyncio
import hashlib
import random
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── USERS DATA ──────────────────────────────────────────────────────────────

USERS = [
    # Admin
    {
        "email": "admin@claimflow.vn",
        "password": "Admin1234!",
        "full_name": "Nguyễn Quản Trị",
        "role": "admin",
        "province": "Hà Nội",
        "region": "north",
    },
    # Reviewers
    {
        "email": "reviewer1@claimflow.vn",
        "password": "Review1234!",
        "full_name": "Trần Thị Bình",
        "role": "reviewer",
        "province": "Hà Nội",
        "region": "north",
    },
    {
        "email": "reviewer2@claimflow.vn",
        "password": "Review1234!",
        "full_name": "Lê Minh Tuấn",
        "role": "reviewer",
        "province": "Hồ Chí Minh",
        "region": "south",
    },
    # Regular users — đa dạng vùng miền
    {
        "email": "user.quangbinh@test.vn",
        "password": "User1234!",
        "full_name": "Nguyễn Văn An",
        "role": "user",
        "province": "Quảng Bình",
        "region": "central",
    },
    {
        "email": "user.hatinh@test.vn",
        "password": "User1234!",
        "full_name": "Phạm Thị Hoa",
        "role": "user",
        "province": "Hà Tĩnh",
        "region": "central",
    },
    {
        "email": "user.hanoi@test.vn",
        "password": "User1234!",
        "full_name": "Trần Đức Mạnh",
        "role": "user",
        "province": "Hà Nội",
        "region": "north",
    },
    {
        "email": "user.hcm@test.vn",
        "password": "User1234!",
        "full_name": "Lê Thị Thu",
        "role": "user",
        "province": "Hồ Chí Minh",
        "region": "south",
    },
    {
        "email": "user.danang@test.vn",
        "password": "User1234!",
        "full_name": "Võ Văn Hùng",
        "role": "user",
        "province": "Đà Nẵng",
        "region": "central",
    },
    {
        "email": "user.nghean@test.vn",
        "password": "User1234!",
        "full_name": "Hoàng Thị Lan",
        "role": "user",
        "province": "Nghệ An",
        "region": "central",
    },
    {
        "email": "user.cantho@test.vn",
        "password": "User1234!",
        "full_name": "Đặng Văn Nam",
        "role": "user",
        "province": "Cần Thơ",
        "region": "south",
    },
    {
        "email": "user.quangnam@test.vn",
        "password": "User1234!",
        "full_name": "Bùi Thị Mai",
        "role": "user",
        "province": "Quảng Nam",
        "region": "central",
    },
    {
        "email": "user.haiphong@test.vn",
        "password": "User1234!",
        "full_name": "Phan Văn Đức",
        "role": "user",
        "province": "Hải Phòng",
        "region": "north",
    },
]

# ── GEO RISK DATA — 64 tỉnh ─────────────────────────────────────────────────

HIGH_RISK_CENTRAL = [
    ("Quảng Bình", "QB", 17.47, 106.62, 92, ["storm","flood","landslide"]),
    ("Hà Tĩnh", "HT", 18.34, 105.90, 90, ["storm","flood","landslide"]),
    ("Nghệ An", "NA", 19.23, 104.92, 87, ["storm","flood","landslide"]),
    ("Quảng Nam", "QNa", 15.57, 108.05, 86, ["storm","flood","landslide"]),
    ("Thừa Thiên Huế", "TTH", 16.46, 107.59, 84, ["storm","flood","inundation"]),
    ("Quảng Ngãi", "QNg", 15.12, 108.79, 83, ["storm","flood","landslide"]),
    ("Bình Định", "BD", 13.78, 109.22, 80, ["storm","flood","drought"]),
    ("Phú Yên", "PY", 13.09, 109.09, 76, ["storm","flood","drought"]),
    ("Khánh Hòa", "KH", 12.24, 109.19, 72, ["storm","drought"]),
    ("Ninh Thuận", "NiT", 11.56, 108.99, 70, ["drought","storm"]),
    ("Bình Thuận", "BiT", 11.09, 108.07, 68, ["drought","storm"]),
    ("Quảng Trị", "QTr", 16.75, 107.18, 82, ["storm","flood","landslide"]),
    ("Đà Nẵng", "DN", 16.05, 108.20, 71, ["storm","flood","inundation"]),
    ("Kon Tum", "KoT", 14.35, 107.99, 65, ["flood","landslide"]),
    ("Gia Lai", "GL", 13.98, 108.00, 62, ["flood","drought"]),
    ("Đắk Lắk", "DL", 12.67, 108.05, 60, ["flood","drought"]),
    ("Đắk Nông", "DN2", 12.00, 107.69, 58, ["flood","landslide"]),
    ("Lâm Đồng", "LDo", 11.94, 108.44, 55, ["landslide","flood"]),
]

MED_RISK_NORTH = [
    ("Hà Nội", "HN", 21.02, 105.84, 35, ["flood","inundation"]),
    ("Hải Phòng", "HP", 20.86, 106.68, 42, ["storm","flood","inundation"]),
    ("Quảng Ninh", "QNi", 21.25, 107.41, 48, ["storm","flood"]),
    ("Hải Dương", "HDu", 20.94, 106.33, 30, ["flood"]),
    ("Hưng Yên", "HY", 20.65, 106.06, 28, ["flood","inundation"]),
    ("Thái Bình", "TB", 20.45, 106.34, 32, ["flood","inundation","storm"]),
    ("Nam Định", "NĐ", 20.42, 106.17, 35, ["flood","inundation"]),
    ("Ninh Bình", "NB", 20.25, 105.97, 33, ["flood"]),
    ("Thanh Hóa", "THo", 19.81, 105.78, 58, ["flood","storm","landslide"]),
    ("Hà Nam", "HNam", 20.58, 105.91, 28, ["flood","inundation"]),
    ("Vĩnh Phúc", "VP", 21.36, 105.60, 25, ["flood"]),
    ("Bắc Ninh", "BNi", 21.19, 106.07, 22, ["flood","inundation"]),
    ("Bắc Giang", "BG", 21.28, 106.19, 28, ["flood","landslide"]),
    ("Phú Thọ", "PT", 21.40, 105.22, 35, ["flood","landslide"]),
    ("Thái Nguyên", "TN", 21.59, 105.85, 32, ["flood","landslide"]),
    ("Lào Cai", "LC", 22.49, 103.97, 58, ["landslide","flood"]),
    ("Yên Bái", "YB", 21.72, 104.91, 52, ["landslide","flood"]),
    ("Sơn La", "SL", 21.33, 103.91, 55, ["landslide","drought","flood"]),
    ("Điện Biên", "ĐBi", 21.39, 103.02, 60, ["landslide","flood"]),
    ("Lai Châu", "LCh", 22.39, 103.46, 65, ["landslide","flood"]),
    ("Hòa Bình", "HBi", 20.82, 105.34, 45, ["flood","landslide"]),
    ("Hà Giang", "HG", 22.82, 105.00, 62, ["landslide","flood"]),
    ("Tuyên Quang", "TQ", 21.82, 105.22, 40, ["flood","landslide"]),
    ("Cao Bằng", "CB", 22.66, 106.26, 45, ["flood","landslide"]),
    ("Bắc Kạn", "BK", 22.14, 105.84, 40, ["flood","landslide"]),
    ("Lạng Sơn", "LS", 21.85, 106.76, 35, ["flood"]),
]

LOW_RISK_SOUTH = [
    ("Hồ Chí Minh", "HCM", 10.82, 106.63, 30, ["flood","inundation"]),
    ("Bình Dương", "BiDu", 11.32, 106.48, 25, ["flood"]),
    ("Đồng Nai", "ĐN", 11.07, 107.17, 28, ["flood"]),
    ("Bà Rịa Vũng Tàu", "BRVT", 10.54, 107.24, 35, ["storm","flood"]),
    ("Tây Ninh", "TaY", 11.36, 106.10, 22, ["drought","flood"]),
    ("Bình Phước", "BP", 11.75, 106.73, 25, ["drought","flood"]),
    ("Long An", "LA", 10.69, 106.24, 32, ["flood","inundation"]),
    ("Tiền Giang", "TiG", 10.36, 106.36, 35, ["flood","inundation"]),
    ("Bến Tre", "BeT", 10.24, 106.38, 38, ["flood","inundation","storm"]),
    ("Trà Vinh", "TV", 9.95, 106.34, 36, ["flood","inundation"]),
    ("Vĩnh Long", "VL", 10.24, 105.97, 34, ["flood","inundation"]),
    ("Đồng Tháp", "ĐT", 10.49, 105.63, 42, ["flood","inundation"]),
    ("An Giang", "AG", 10.52, 105.12, 40, ["flood","inundation"]),
    ("Kiên Giang", "KG", 10.01, 105.08, 45, ["flood","storm","inundation"]),
    ("Cần Thơ", "CT", 10.03, 105.79, 35, ["flood","inundation"]),
    ("Hậu Giang", "HGi", 9.79, 105.64, 33, ["flood","inundation"]),
    ("Sóc Trăng", "ST", 9.60, 105.97, 37, ["flood","inundation"]),
    ("Bạc Liêu", "BLi", 9.29, 105.73, 40, ["flood","storm"]),
    ("Cà Mau", "CM", 9.18, 105.15, 45, ["storm","flood","inundation"]),
]

ALL_PROVINCES = HIGH_RISK_CENTRAL + MED_RISK_NORTH + LOW_RISK_SOUTH

DISASTER_TYPES = {
    "storm": {"vi": "Bão"},
    "flood": {"vi": "Lũ lụt"},
    "landslide": {"vi": "Sạt lở đất"},
    "inundation": {"vi": "Ngập úng"},
    "drought": {"vi": "Hạn hán"},
}

INSURANCE_RECS = {
    "storm":     ("Bảo hiểm bão lũ", "Tỉnh nằm trên đường đi của bão"),
    "flood":     ("Bảo hiểm lũ lụt", "Khu vực thường xuyên ngập lụt"),
    "landslide": ("Bảo hiểm thiên tai toàn diện", "Địa hình đồi núi, nguy cơ sạt lở"),
    "inundation":("Bảo hiểm ngập nước nhà ở", "Vùng trũng thấp dễ bị ngập"),
    "drought":   ("Bảo hiểm nông nghiệp", "Khí hậu khô hạn ảnh hưởng mùa vụ"),
}

# ── POLICIES ─────────────────────────────────────────────────────────────────

POLICIES = [
    {
        "title": "Điều khoản bảo hiểm y tế 2024",
        "category": "medical",
        "coverage_types": ["medical", "dental", "hospitalization"],
        "version": "2024.1",
        "content": """
# Điều Khoản Bảo Hiểm Y Tế 2024

## 1. Phạm vi bảo hiểm

### Nhóm bệnh hô hấp (ICD-10: J00–J99)
- J18.1 — Viêm phổi thùy: tối đa 5,000,000 VND/đợt
- J06.9 — Viêm đường hô hấp cấp: tối đa 2,000,000 VND/đợt
- J45.0 — Hen phế quản: tối đa 3,000,000 VND/đợt

### Nhóm bệnh tiêu hóa (ICD-10: K00–K95)
- K29.7 — Viêm dạ dày: tối đa 2,000,000 VND/đợt
- K35.9 — Viêm ruột thừa cấp: tối đa 15,000,000 VND/đợt

### Nhóm tim mạch (ICD-10: I00–I99)
- I10 — Tăng huyết áp: tối đa 3,000,000 VND/đợt

## 2. Giới hạn bảo hiểm
- Ngoại trú: tối đa 3,000,000 VND/đợt, 20,000,000 VND/năm
- Nội trú: tối đa 50,000,000 VND/đợt, 200,000,000 VND/năm
- Tổng năm: 500,000,000 VND

## 3. KHÔNG bảo hiểm
- Điều trị thẩm mỹ không do tai nạn
- Mang thai và sinh đẻ bình thường
- Rối loạn tâm thần (gói cơ bản)
- Bệnh có sẵn trong 12 tháng đầu (pre-existing conditions)

## 4. Yêu cầu hồ sơ
- Hóa đơn viện phí có dấu đỏ
- Đơn thuốc bác sĩ ký
- Giấy ra viện (nội trú)
- Nộp trong 90 ngày kể từ ngày điều trị
        """.strip(),
    },
    {
        "title": "Điều khoản bảo hiểm thiên tai 2024",
        "category": "disaster",
        "coverage_types": ["flood", "storm", "landslide", "inundation"],
        "version": "2024.1",
        "content": """
# Điều Khoản Bảo Hiểm Thiên Tai 2024

## 1. Phạm vi bảo hiểm thiên tai

### Bão và lũ lụt
- Thiệt hại nhà ở do bão: tối đa 100,000,000 VND
- Thiệt hại tài sản do lũ: tối đa 50,000,000 VND
- Chi phí di dời khẩn cấp: tối đa 10,000,000 VND
- Hỗ trợ sinh hoạt trong thời gian sửa chữa: 1,000,000 VND/ngày, tối đa 30 ngày

### Sạt lở đất
- Thiệt hại nhà ở: tối đa 150,000,000 VND
- Thiệt hại đất canh tác: tối đa 30,000,000 VND

### Ngập úng đô thị
- Thiệt hại đồ dùng, thiết bị: tối đa 20,000,000 VND
- Thiệt hại xe máy, ô tô: theo giá trị thực tế, tối đa 200,000,000 VND

## 2. Điều kiện áp dụng
- Thiên tai được Chính phủ hoặc cơ quan có thẩm quyền công nhận
- Thiệt hại phải được ghi nhận bởi chính quyền địa phương
- Thông báo trong 72 giờ sau sự kiện

## 3. Tỉnh có hệ số rủi ro cao (phí bảo hiểm cao hơn 20-30%)
Quảng Bình, Hà Tĩnh, Nghệ An, Quảng Nam, Thừa Thiên Huế,
Quảng Ngãi, Bình Định, Quảng Trị, Lào Cai, Sơn La

## 4. KHÔNG bảo hiểm
- Thiệt hại do chiến tranh, bạo loạn
- Thiệt hại do hỏa hoạn (có gói riêng)
- Công trình không có phép xây dựng
- Tài sản không khai báo khi mua bảo hiểm
        """.strip(),
    },
    {
        "title": "Điều khoản bảo hiểm nha khoa 2024",
        "category": "dental",
        "coverage_types": ["dental"],
        "version": "2024.1",
        "content": """
# Điều Khoản Bảo Hiểm Nha Khoa 2024

## 1. Dịch vụ được bảo hiểm

### Điều trị cơ bản (100%)
- Kiểm tra răng định kỳ: 2 lần/năm, tối đa 500,000 VND/lần
- Cạo vôi răng: 2 lần/năm, tối đa 500,000 VND/lần
- Trám răng sâu: tối đa 1,000,000 VND/răng, tối đa 5 răng/năm
- Nhổ răng đơn giản: tối đa 800,000 VND/răng

### Điều trị chuyên sâu (70%)
- Điều trị tủy răng: tối đa 3,000,000 VND/răng
- Nhổ răng khôn: tối đa 2,000,000 VND/răng

## 2. Giới hạn năm
- Điều trị cơ bản: 10,000,000 VND/năm
- Điều trị chuyên sâu: 20,000,000 VND/năm
- Tổng: 50,000,000 VND/năm

## 3. KHÔNG bảo hiểm
- Niềng răng thẩm mỹ
- Tẩy trắng răng
- Implant răng
- Dán sứ veneer
        """.strip(),
    },
]

# ── CLAIMS DATA ──────────────────────────────────────────────────────────────

CLAIMS_TEMPLATES = [
    # APPROVED — viêm phổi
    {
        "claim_type": "medical",
        "status": "approved",
        "amount_claimed": 2600000,
        "amount_approved": 2600000,
        "province": "Hà Nội",
        "disaster_type": None,
        "ai_decision": "approved",
        "ai_fraud_score": 8,
        "ai_fraud_flags": [],
        "ai_reasoning": "ICD J18.1 thuộc nhóm bệnh hô hấp được bảo hiểm. Mức tối đa 5,000,000 VND. Số tiền yêu cầu 2,600,000 VND trong giới hạn. Không phát hiện dấu hiệu gian lận.",
        "ai_parsed_data": {"diagnosis": "Viêm phổi thùy phải", "icd_code": "J18.1", "doctor": "BS. Trần Minh Tuấn", "hospital": "Bệnh viện Bạch Mai"},
    },
    # REJECTED — thẩm mỹ
    {
        "claim_type": "medical",
        "status": "rejected",
        "amount_claimed": 18000000,
        "amount_approved": 0,
        "province": "Hồ Chí Minh",
        "disaster_type": None,
        "ai_decision": "rejected",
        "ai_fraud_score": 5,
        "ai_fraud_flags": [],
        "ai_reasoning": "Dịch vụ 'Nâng mũi cấu trúc sụn' là phẫu thuật thẩm mỹ không do tai nạn, thuộc danh mục KHÔNG được bảo hiểm theo Điều 3.",
        "ai_parsed_data": {"service": "Nâng mũi cấu trúc sụn tự thân", "facility": "Thẩm mỹ viện ABC"},
    },
    # MANUAL REVIEW — fraud cao
    {
        "claim_type": "medical",
        "status": "manual_review",
        "amount_claimed": 30000000,
        "amount_approved": None,
        "province": "Hà Nội",
        "disaster_type": None,
        "ai_decision": "manual_review",
        "ai_fraud_score": 85,
        "ai_fraud_flags": ["amount_anomaly", "provider_not_whitelisted"],
        "ai_reasoning": "Phát hiện bất thường: (1) Chi phí 30,000,000 VND cho đau đầu thông thường G44.2 bất thường — thông thường dưới 500,000 VND. (2) Phòng khám XYZ không có trong danh sách cơ sở hợp lệ.",
        "ai_parsed_data": {"diagnosis": "Đau đầu thông thường", "icd_code": "G44.2", "facility": "Phòng khám XYZ"},
    },
    # APPROVED — lũ lụt Quảng Bình
    {
        "claim_type": "disaster",
        "status": "approved",
        "amount_claimed": 45000000,
        "amount_approved": 42000000,
        "province": "Quảng Bình",
        "disaster_type": "flood",
        "ai_decision": "approved",
        "ai_fraud_score": 12,
        "ai_fraud_flags": [],
        "ai_reasoning": "Lũ lụt tháng 10/2024 tại Quảng Bình được UBND tỉnh công nhận là thiên tai. Thiệt hại nhà ở 45,000,000 VND trong giới hạn bảo hiểm. Hồ sơ đầy đủ.",
        "ai_parsed_data": {"disaster_type": "Lũ lụt", "damage_type": "Nhà ở bị ngập", "province": "Quảng Bình"},
    },
    # APPROVED — bão Hà Tĩnh
    {
        "claim_type": "disaster",
        "status": "approved",
        "amount_claimed": 28000000,
        "amount_approved": 25000000,
        "province": "Hà Tĩnh",
        "disaster_type": "storm",
        "ai_decision": "approved",
        "ai_fraud_score": 15,
        "ai_fraud_flags": [],
        "ai_reasoning": "Bão số 4 (2024) ảnh hưởng trực tiếp tỉnh Hà Tĩnh. Thiệt hại mái nhà và tài sản 28,000,000 VND. Hồ sơ hợp lệ.",
        "ai_parsed_data": {"disaster_type": "Bão", "storm_name": "Bão số 4/2024", "damage": "Mái nhà, tài sản"},
    },
    # MANUAL REVIEW — lũ amount cao
    {
        "claim_type": "disaster",
        "status": "manual_review",
        "amount_claimed": 180000000,
        "amount_approved": None,
        "province": "Nghệ An",
        "disaster_type": "landslide",
        "ai_decision": "manual_review",
        "ai_fraud_score": 72,
        "ai_fraud_flags": ["amount_high", "missing_government_cert"],
        "ai_reasoning": "Số tiền 180,000,000 VND cao bất thường. Thiếu giấy xác nhận thiệt hại từ UBND xã/phường. Cần reviewer xác minh thực địa.",
        "ai_parsed_data": {"disaster_type": "Sạt lở đất", "claimed_damage": "Toàn bộ ngôi nhà"},
    },
    # PENDING — mới submit
    {
        "claim_type": "medical",
        "status": "pending",
        "amount_claimed": 3200000,
        "amount_approved": None,
        "province": "Đà Nẵng",
        "disaster_type": None,
        "ai_decision": None,
        "ai_fraud_score": None,
        "ai_fraud_flags": [],
        "ai_reasoning": None,
        "ai_parsed_data": None,
    },
    # APPROVED — nha khoa
    {
        "claim_type": "dental",
        "status": "approved",
        "amount_claimed": 1550000,
        "amount_approved": 1550000,
        "province": "Hồ Chí Minh",
        "disaster_type": None,
        "ai_decision": "approved",
        "ai_fraud_score": 10,
        "ai_fraud_flags": [],
        "ai_reasoning": "Trám răng và cạo vôi thuộc nhóm điều trị nha khoa cơ bản được bảo hiểm 100%. Phòng khám Smile có giấy phép SYT hợp lệ.",
        "ai_parsed_data": {"services": ["Trám răng số 6", "Cạo vôi răng"], "facility": "Nha khoa Smile"},
    },
    # REJECTED — thiên tai không được công nhận
    {
        "claim_type": "disaster",
        "status": "rejected",
        "amount_claimed": 15000000,
        "amount_approved": 0,
        "province": "Cần Thơ",
        "disaster_type": "inundation",
        "ai_decision": "rejected",
        "ai_fraud_score": 20,
        "ai_fraud_flags": [],
        "ai_reasoning": "Ngập úng ngày 15/05/2024 tại Cần Thơ không nằm trong danh sách thiên tai được UBND tỉnh công nhận. Không đủ điều kiện bồi thường theo Điều 2.",
        "ai_parsed_data": {"disaster_type": "Ngập úng", "date": "15/05/2024"},
    },
    # PROCESSING — đang xử lý
    {
        "claim_type": "disaster",
        "status": "processing",
        "amount_claimed": 35000000,
        "amount_approved": None,
        "province": "Quảng Nam",
        "disaster_type": "flood",
        "ai_decision": None,
        "ai_fraud_score": None,
        "ai_fraud_flags": [],
        "ai_reasoning": None,
        "ai_parsed_data": None,
    },
]

# ── CHAT SESSIONS ─────────────────────────────────────────────────────────────

CHAT_SESSIONS = [
    {
        "messages": [
            {"role": "user", "content": "Tôi ở Quảng Bình, tôi cần mua bảo hiểm gì?"},
            {"role": "assistant", "content": "Vì bạn ở tỉnh Bắc Trung Bộ — khu vực có rủi ro thiên tai cao nhất Việt Nam, tôi khuyến nghị:\n\n1. **Bảo hiểm bão lũ** (ưu tiên cao nhất, 95%) — Quảng Bình nằm trực tiếp trên đường đi của bão Tây Bắc Thái Bình Dương\n2. **Bảo hiểm nhà ở toàn diện** (88%) — nguy cơ ngập lụt và sạt lở đất cao\n3. **Bảo hiểm nông nghiệp** (82%) — thiệt hại mùa vụ thường xuyên\n\nBạn muốn tôi giải thích chi tiết về gói nào không?"},
            {"role": "user", "content": "Gói bảo hiểm bão lũ bao gồm những gì?"},
            {"role": "assistant", "content": "Gói bảo hiểm bão lũ của chúng tôi bao gồm:\n\n**Thiệt hại nhà ở:** tối đa 100,000,000 VND do bão trực tiếp phá hủy\n**Thiệt hại tài sản do lũ:** tối đa 50,000,000 VND\n**Chi phí di dời khẩn cấp:** tối đa 10,000,000 VND\n**Hỗ trợ sinh hoạt:** 1,000,000 VND/ngày trong thời gian sửa chữa (tối đa 30 ngày)\n\nĐiều kiện: thiên tai phải được chính quyền địa phương công nhận và thông báo trong 72 giờ sau sự kiện."},
        ]
    },
    {
        "messages": [
            {"role": "user", "content": "Làm thế nào để nộp hồ sơ bồi thường bảo hiểm y tế?"},
            {"role": "assistant", "content": "Quy trình nộp hồ sơ bồi thường y tế rất đơn giản:\n\n**Bước 1:** Upload tài liệu lên hệ thống ClaimFlow:\n- Hóa đơn viện phí (có dấu đỏ bệnh viện)\n- Đơn thuốc bác sĩ ký\n- Kết quả xét nghiệm (nếu có)\n\n**Bước 2:** Hệ thống AI sẽ tự động:\n- Đọc và trích xuất thông tin từ tài liệu\n- Kiểm tra điều khoản bảo hiểm\n- Đưa ra quyết định trong 30 phút\n\n**Bước 3:** Nhận kết quả qua email và thông báo trên app\n\n**Lưu ý:** Hồ sơ phải nộp trong **90 ngày** kể từ ngày điều trị."},
        ]
    },
]

# ── AUDIT LOGS MẪU ────────────────────────────────────────────────────────────

AUDIT_ACTIONS = [
    ("role_change", "user", {"old_role": "user", "new_role": "reviewer", "reason": "Promoted to claims reviewer team"}),
    ("policy_upload", "policy", {"title": "Điều khoản bảo hiểm thiên tai 2024", "category": "disaster", "chunks": 52}),
    ("claim_override", "claim", {"old_decision": "manual_review", "new_decision": "approved", "note": "Đã xác minh thiệt hại thực tế"}),
    ("user_deactivate", "user", {"reason": "Tài khoản vi phạm điều khoản sử dụng"}),
    ("policy_delete", "policy", {"title": "Điều khoản cũ 2023", "reason": "Hết hạn, thay bằng phiên bản 2024"}),
]

# ═══════════════════════════════════════════════════════════════
# MAIN SEED FUNCTION
# ═══════════════════════════════════════════════════════════════

async def seed():
    from motor.motor_asyncio import AsyncIOMotorClient
    from beanie import init_beanie, Document
    from pydantic import EmailStr, Field
    from typing import Literal
    import uuid

    print("\n🌱 ClaimFlow — Seeding test data...\n")

    # Connect MongoDB
    client = AsyncIOMotorClient("mongodb://admin:admin@localhost:27017")
    db = client["claimflow_db"]

    # Drop và tạo lại collections (fresh seed)
    print("🗑️  Clearing existing data...")
    for col in ["users", "documents", "claims", "geo_risks", "chat_sessions", "policies", "audit_logs"]:
        await db[col].drop()

    # ── 1. USERS ──────────────────────────────────────────────────────────────
    print("👤 Creating users...")
    user_ids = {}
    for u in USERS:
        doc = {
            "_id": str(uuid.uuid4()),
            "email": u["email"],
            "hashed_password": pwd_context.hash(u["password"]),
            "full_name": u["full_name"],
            "role": u["role"],
            "province": u["province"],
            "region": u["region"],
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=random.randint(10, 90)),
            "updated_at": datetime.utcnow(),
        }
        await db.users.insert_one(doc)
        user_ids[u["email"]] = doc["_id"]
        role_icon = {"admin": "👑", "reviewer": "🔍", "user": "👤"}[u["role"]]
        print(f"  {role_icon} {u['role']:8} — {u['email']:35} (pw: {u['password']})")

    # ── 2. GEO RISKS — 64 tỉnh ──────────────────────────────────────────────
    print("\n🗺️  Creating geo risk data (64 provinces)...")
    for prov in ALL_PROVINCES:
        name, code, lat, lng, score, disasters = prov
        region = "central" if prov in HIGH_RISK_CENTRAL else ("north" if prov in MED_RISK_NORTH else "south")
        is_high = score >= 70

        disaster_risks = []
        for d in disasters:
            disaster_risks.append({
                "type": d,
                "risk_score": min(100, score + random.randint(-10, 5)),
                "frequency": "high" if score >= 80 else ("medium" if score >= 60 else "low"),
                "historical_events": random.randint(5, 60) if is_high else random.randint(1, 20),
            })

        recommendations = []
        for d in disasters[:3]:
            ins_type, reason = INSURANCE_RECS.get(d, ("Bảo hiểm thiên tai", "Rủi ro thiên tai"))
            recommendations.append({
                "insurance_type": ins_type,
                "priority_score": min(100, score + random.randint(-5, 5)),
                "reason": reason,
                "estimated_premium": f"{random.randint(1,3)},000,000 - {random.randint(3,8)},000,000 VND/năm",
            })

        doc = {
            "_id": str(uuid.uuid4()),
            "province_name": name,
            "province_code": code,
            "lat": lat,
            "lng": lng,
            "region": region,
            "overall_risk_score": score,
            "is_high_risk": is_high,
            "risk_factors": ["typhoon_path" if "storm" in disasters else None,
                            "flood_prone" if "flood" in disasters else None,
                            "mountainous" if "landslide" in disasters else None],
            "disaster_risks": disaster_risks,
            "recommendations": recommendations,
            "last_updated": datetime.utcnow(),
        }
        doc["risk_factors"] = [f for f in doc["risk_factors"] if f]
        await db.geo_risks.insert_one(doc)

    high_count = sum(1 for p in ALL_PROVINCES if p[4] >= 70)
    print(f"  ✅ {len(ALL_PROVINCES)} provinces seeded ({high_count} high-risk)")

    # ── 3. POLICIES ──────────────────────────────────────────────────────────
    print("\n📋 Creating policy documents...")
    policy_ids = []
    for p in POLICIES:
        doc = {
            "_id": str(uuid.uuid4()),
            "title": p["title"],
            "content": p["content"],
            "category": p["category"],
            "coverage_types": p["coverage_types"],
            "version": p["version"],
            "is_active": True,
            "chunk_count": len(p["content"]) // 500 + 1,  # Estimated
            "last_ingested": datetime.utcnow(),
            "created_at": datetime.utcnow(),
        }
        await db.policies.insert_one(doc)
        policy_ids.append(doc["_id"])
        print(f"  📄 {p['category']:10} — {p['title']}")

    # ── 4. CLAIMS ─────────────────────────────────────────────────────────────
    print("\n📝 Creating claims...")
    regular_users = [email for email, uid in user_ids.items() if "user." in email]
    claim_ids = []

    for i, tmpl in enumerate(CLAIMS_TEMPLATES):
        user_email = regular_users[i % len(regular_users)]
        user_id = user_ids[user_email]
        days_ago = random.randint(1, 60)
        created = datetime.utcnow() - timedelta(days=days_ago)
        processed = (created + timedelta(minutes=random.randint(5, 30))
                    if tmpl["status"] not in ["pending", "processing"] else None)

        # Reviewer assignment for manual_review claims
        reviewer_id = None
        reviewer_note = None
        reviewed_at = None
        if tmpl["status"] in ["approved", "rejected"] and random.random() > 0.6:
            reviewer_id = user_ids.get("reviewer1@claimflow.vn")
            reviewer_note = "Đã xác minh hồ sơ hợp lệ." if tmpl["status"] == "approved" else "Không đủ điều kiện bảo hiểm."
            reviewed_at = processed + timedelta(hours=2) if processed else None

        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_id,
            "status": tmpl["status"],
            "claim_type": tmpl["claim_type"],
            "description": f"Yêu cầu bồi thường {tmpl['claim_type']} — {tmpl.get('province', 'N/A')}",
            "amount_claimed": tmpl["amount_claimed"],
            "amount_approved": tmpl["amount_approved"],
            "province": tmpl.get("province"),
            "disaster_type": tmpl.get("disaster_type"),
            "ai_decision": tmpl["ai_decision"],
            "ai_reasoning": tmpl["ai_reasoning"],
            "ai_fraud_score": tmpl["ai_fraud_score"],
            "ai_fraud_flags": tmpl["ai_fraud_flags"],
            "ai_parsed_data": tmpl["ai_parsed_data"],
            "reviewer_id": reviewer_id,
            "reviewer_note": reviewer_note,
            "reviewed_at": reviewed_at,
            "documents": [],
            "created_at": created,
            "processed_at": processed,
            "updated_at": processed or created,
        }
        await db.claims.insert_one(doc)
        claim_ids.append(doc["_id"])
        status_icon = {"approved":"✅","rejected":"❌","manual_review":"⚠️","pending":"⏳","processing":"🔄"}
        print(f"  {status_icon.get(tmpl['status'],'?')} {tmpl['status']:15} {tmpl['claim_type']:12} — {tmpl['amount_claimed']:>12,} VND")

    # ── 5. CHAT SESSIONS ──────────────────────────────────────────────────────
    print("\n💬 Creating chat sessions...")
    for i, session in enumerate(CHAT_SESSIONS):
        user_email = regular_users[i % len(regular_users)]
        messages = []
        base_time = datetime.utcnow() - timedelta(hours=random.randint(1, 48))
        for j, msg in enumerate(session["messages"]):
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": base_time + timedelta(minutes=j * 2),
            })
        doc = {
            "_id": str(uuid.uuid4()),
            "user_id": user_ids[user_email],
            "messages": messages,
            "message_count": len(messages),
            "context": {"province": regular_users[i % len(regular_users)].split("@")[0].replace("user.", "")},
            "created_at": base_time,
            "updated_at": base_time + timedelta(minutes=len(messages) * 2),
        }
        await db.chat_sessions.insert_one(doc)
    print(f"  ✅ {len(CHAT_SESSIONS)} chat sessions created")

    # ── 6. AUDIT LOGS ─────────────────────────────────────────────────────────
    print("\n📊 Creating audit logs...")
    admin_id = user_ids["admin@claimflow.vn"]
    for action, target_type, details in AUDIT_ACTIONS:
        target_id = (user_ids.get("reviewer1@claimflow.vn") if target_type == "user"
                    else (claim_ids[0] if target_type == "claim"
                    else policy_ids[0] if policy_ids else str(uuid.uuid4())))
        doc = {
            "_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow() - timedelta(hours=random.randint(1, 72)),
            "actor_id": admin_id,
            "actor_email": "admin@claimflow.vn",
            "action": action,
            "target_type": target_type,
            "target_id": str(target_id),
            "details": details,
            "ip_address": "127.0.0.1",
        }
        await db.audit_logs.insert_one(doc)
    print(f"  ✅ {len(AUDIT_ACTIONS)} audit logs created")

    # ── SUMMARY ──────────────────────────────────────────────────────────────
    print("\n" + "="*55)
    print("✅ Seed completed!")
    print("="*55)
    print(f"  👤 Users:        {len(USERS)}")
    print(f"  🗺️  Geo Risks:    {len(ALL_PROVINCES)} provinces")
    print(f"  📋 Policies:     {len(POLICIES)}")
    print(f"  📝 Claims:       {len(CLAIMS_TEMPLATES)}")
    print(f"  💬 Chat sessions:{len(CHAT_SESSIONS)}")
    print(f"  📊 Audit logs:   {len(AUDIT_ACTIONS)}")
    print("="*55)
    print("\n📌 Test accounts:")
    print("  👑 admin@claimflow.vn        / Admin1234!")
    print("  🔍 reviewer1@claimflow.vn    / Review1234!")
    print("  🔍 reviewer2@claimflow.vn    / Review1234!")
    print("  👤 user.quangbinh@test.vn    / User1234!")
    print("  👤 user.hatinh@test.vn       / User1234!")
    print("  👤 user.hanoi@test.vn        / User1234!")
    print("  👤 user.hcm@test.vn          / User1234!")
    print("\n🚀 Access:")
    print("  Frontend:  http://localhost:3000")
    print("  API Docs:  http://localhost:8000/docs")
    print("  Mongo UI:  http://localhost:8081")
    print("  Qdrant:    http://localhost:6333/dashboard")

    client.close()

if __name__ == "__main__":
    asyncio.run(seed())
