# SCHEMA.md — Database Schema (MongoDB)

> Full schema reference. Claude đọc file này trước khi viết query, model, hay index.
> **ODM:** Beanie (async, built trên Motor + Pydantic)

---

## Collections overview

```
users         ── claims (ref)
users         ── documents (ref)
users         ── chat_sessions (ref)
documents     ── claims.documents (embedded ref)
policies      ── Qdrant vectors (ingested separately)
geo_risks     ── standalone (province static + dynamic data)
```

---

## Collection: `users`

```python
class User(Document):
    email: Indexed(EmailStr, unique=True)
    hashed_password: str
    full_name: str | None = None
    role: Literal["user", "reviewer", "admin"] = "user"
    province: str | None = None        # Tỉnh/thành phố
    region: Literal["north", "central", "south"] | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "users"
        indexes = [("email", 1), ("role", 1), ("province", 1)]
```

---

## Collection: `documents`

Document OCR — kết quả phân tích tài liệu từ Gemini Vision.

```python
class ExtractedField(BaseModel):
    key: str
    value: str | None
    confidence: float          # 0.0 - 1.0
    bbox: list[float] | None   # [x, y, w, h] — cho visual highlighting

class DocumentEmbed(BaseModel):
    """Embedded trong Claim — reference ngắn gọn"""
    id: str
    doc_type: str
    file_name: str
    created_at: datetime

class Document(Document):
    user_id: str
    file_name: str
    file_key: str              # S3/MinIO key
    file_hash: str             # MD5 hash — dùng cho OCR cache
    file_type: Literal["pdf", "jpg", "jpeg", "png"]
    file_size_kb: int

    doc_type: Literal[
        "cccd", "cmnd", "driver_license", "passport",
        "vehicle_registration", "insurance_policy", "other"
    ]

    # OCR Results
    raw_text: str | None = None
    extracted_fields: list[ExtractedField] = []
    structured_data: dict = {}
    ocr_confidence: float | None = None        # Overall confidence 0.0-1.0
    needs_manual_review: bool = False          # True khi confidence < 0.7
    low_confidence_fields: list[str] = []      # Fields cần user xác nhận

    # Edit history — version tracking
    version: int = 1
    edit_history: list[dict] = []   # [{field, old_value, new_value, edited_by, timestamp}]

    # Merge info
    is_merged: bool = False
    merged_from: list[str] = []
    merged_data: dict = {}

    # Export
    export_json: str | None = None
    export_markdown: str | None = None

    processing_status: Literal["pending", "processing", "done", "failed"] = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "documents"
        indexes = [
            ("user_id", 1), ("doc_type", 1),
            ("processing_status", 1),
            ("file_hash", 1),      # Cho OCR cache lookup
        ]
```

### structured_data format theo doc_type

**CCCD:**
```json
{
  "id_number": "001234567890",
  "full_name": "NGUYỄN VĂN AN",
  "date_of_birth": "15/03/1990",
  "sex": "Nam",
  "nationality": "Việt Nam",
  "place_of_origin": "Hà Nội",
  "place_of_residence": "45 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội",
  "expiry_date": "15/03/2035"
}
```

**Insurance Policy:**
```json
{
  "policy_number": "BH-2024-001234",
  "insured_name": "Nguyễn Văn An",
  "insurance_type": "Nhân thọ",
  "start_date": "01/01/2024",
  "end_date": "01/01/2034",
  "premium_amount": 5000000,
  "coverage_amount": 500000000,
  "beneficiary": "Nguyễn Thị B"
}
```

---

## Collection: `claims`

```python
class Claim(Document):
    user_id: str
    status: Literal["pending","processing","approved","rejected","manual_review"] = "pending"
    claim_type: Literal["medical","dental","hospitalization","medication","disaster"]

    amount_claimed: float
    amount_approved: float | None = None

    # Embedded document references
    documents: list[DocumentEmbed] = []

    # AI Results
    ai_decision: str | None = None
    ai_reasoning: str | None = None
    ai_fraud_score: int | None = None      # 0-100
    ai_fraud_flags: list[str] = []
    ai_parsed_data: dict | None = None

    # Geo context (nếu claim liên quan thiên tai)
    province: str | None = None
    disaster_type: str | None = None       # "flood", "storm", "landslide"

    # Human Review
    reviewer_id: str | None = None
    reviewer_note: str | None = None
    reviewed_at: datetime | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: datetime | None = None

    class Settings:
        name = "claims"
        indexes = [
            ("user_id", 1), ("status", 1),
            ("province", 1), ("created_at", -1),
            [("user_id", 1), ("status", 1)],
        ]
```

---

## Collection: `geo_risks`

Static data + dynamic risk scores theo tỉnh/thành.

```python
class DisasterRisk(BaseModel):
    type: Literal["storm","flood","landslide","inundation","drought"]
    risk_score: int          # 0-100
    frequency: str           # "high", "medium", "low"
    historical_events: int   # Số sự kiện lịch sử

class InsuranceRecommendation(BaseModel):
    insurance_type: str
    priority_score: int      # 0-100 — bao nhiêu % nên mua
    reason: str

class GeoRisk(Document):
    province_name: str       # "Hà Nội", "Quảng Bình"...
    province_code: str       # "HN", "QB"...
    region: Literal["north", "central", "south"]
    overall_risk_score: int  # 0-100 tổng hợp

    disaster_risks: list[DisasterRisk] = []
    recommendations: list[InsuranceRecommendation] = []

    # High-risk flags
    is_high_risk: bool = False
    risk_factors: list[str] = []   # ["flood_prone", "typhoon_path", "mountainous"]

    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "geo_risks"
        indexes = [("province_name", 1), ("province_code", 1), ("region", 1), ("is_high_risk", 1)]
```

### Ví dụ document Quảng Bình (rủi ro cao)

```json
{
  "province_name": "Quảng Bình",
  "province_code": "QB",
  "region": "central",
  "overall_risk_score": 92,
  "is_high_risk": true,
  "risk_factors": ["typhoon_path", "flood_prone", "mountainous"],
  "disaster_risks": [
    {"type": "storm", "risk_score": 95, "frequency": "high", "historical_events": 47},
    {"type": "flood", "risk_score": 90, "frequency": "high", "historical_events": 38},
    {"type": "landslide", "risk_score": 75, "frequency": "medium", "historical_events": 12}
  ],
  "recommendations": [
    {"insurance_type": "Bảo hiểm bão lũ", "priority_score": 95, "reason": "Nằm trực tiếp trên đường đi của bão"},
    {"insurance_type": "Bảo hiểm nhà ở", "priority_score": 88, "reason": "Nguy cơ ngập lụt và sạt lở cao"},
    {"insurance_type": "Bảo hiểm nông nghiệp", "priority_score": 82, "reason": "Thiệt hại mùa vụ thường xuyên"}
  ]
}
```

---

## Collection: `chat_sessions`

```python
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatSession(Document):
    user_id: str
    messages: list[ChatMessage] = []
    message_count: int = 0             # Counter riêng — tránh đếm array mỗi lần
    context: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    async def add_message(self, message: ChatMessage):
        """Thêm message và giữ tối đa 50 tin gần nhất tránh 16MB limit."""
        if len(self.messages) >= 50:
            self.messages = self.messages[-49:]  # Giữ 49 tin cũ + 1 tin mới
        self.messages.append(message)
        self.message_count += 1
        self.updated_at = datetime.utcnow()
        await self.save()

    class Settings:
        name = "chat_sessions"
        indexes = [("user_id", 1), ("updated_at", -1)]
```

---

## Collection: `policies`

RAG source — được ingest vào Qdrant.

```python
class Policy(Document):
    title: str
    content: str               # Full text cho chunking
    category: str              # "medical", "disaster", "life", "property"
    coverage_types: list[str]  # ["flood", "storm", "landslide"]
    version: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "policies"
        indexes = [("category", 1), ("is_active", 1)]
```

---

## Setup MongoDB

```yaml
# docker-compose.yml
mongodb:
  image: mongo:7.0
  ports: ["27017:27017"]
  environment:
    MONGO_INITDB_ROOT_USERNAME: admin
    MONGO_INITDB_ROOT_PASSWORD: admin
    MONGO_INITDB_DATABASE: claimflow_db
  volumes: [mongodb_data:/data/db]
```

```python
# app/core/database.py
async def init_db(mongodb_url: str, db_name: str):
    client = AsyncIOMotorClient(mongodb_url)
    await init_beanie(
        database=client[db_name],
        document_models=[User, Document, Claim, GeoRisk, ChatSession, Policy],
    )
```

```env
MONGODB_URL=mongodb://admin:admin@localhost:27017
MONGODB_DB_NAME=claimflow_db
```

---

## Query thường dùng

```python
# Lấy risk data theo province
risk = await GeoRisk.find_one(GeoRisk.province_name == province_name)

# Lấy all high-risk provinces cho map
high_risk = await GeoRisk.find(GeoRisk.is_high_risk == True).to_list()

# Chat session của user (latest first)
sessions = await ChatSession.find(
    ChatSession.user_id == user_id
).sort(-ChatSession.updated_at).to_list()

# Claims theo status + province
claims = await Claim.find(
    Claim.user_id == user_id,
    Claim.province == province
).sort(-Claim.created_at).to_list()
```

---

## Collection: `audit_logs`

Ghi lại mọi hành động quan trọng trong hệ thống — chỉ Admin xem được.

```python
class AuditLog(Document):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    actor_id: str                  # User thực hiện hành động
    actor_email: str
    action: Literal[
        "role_change", "user_deactivate", "user_activate",
        "policy_upload", "policy_delete",
        "claim_override", "login_failed", "login_success"
    ]
    target_type: Literal["user", "policy", "claim"]
    target_id: str
    details: dict = {}             # Thông tin chi tiết tùy action
    ip_address: str | None = None

    class Settings:
        name = "audit_logs"
        indexes = [
            ("actor_id", 1),
            ("action", 1),
            ("timestamp", -1),
            ("target_type", 1),
        ]
```

### Cách dùng AuditLog

```python
# Trong service — ghi log sau mỗi action quan trọng
async def change_user_role(admin_id: str, target_user_id: str, new_role: str):
    user = await User.get(target_user_id)
    old_role = user.role
    await user.set({User.role: new_role})
    
    # Ghi audit log
    await AuditLog(
        actor_id=admin_id,
        actor_email=admin.email,
        action="role_change",
        target_type="user",
        target_id=target_user_id,
        details={"old_role": old_role, "new_role": new_role}
    ).insert()
```

---

## Role-based Access — Dependency Injection

```python
# app/api/deps.py

from fastapi import Depends, HTTPException, status
from app.models.user import User

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Verify JWT và trả về user hiện tại."""
    ...

async def require_reviewer(
    current_user: User = Depends(get_current_user)
) -> User:
    """Chỉ cho phép reviewer và admin."""
    if current_user.role not in ["reviewer", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer access required"
        )
    return current_user

async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Chỉ cho phép admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Dùng trong routes:
@router.get("/admin/users")
async def list_users(admin: User = Depends(require_admin)):
    ...

@router.patch("/claims/{id}/review")
async def review_claim(reviewer: User = Depends(require_reviewer)):
    ...
```
