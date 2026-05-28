# TASKS.md — ClaimFlow

> Kế hoạch task chi tiết 4 tuần. Mỗi task có description rõ ràng, output mong đợi, ghi chú kỹ thuật.

**Status:** `[ ]` Chưa | `[~]` Đang | `[x]` Xong
**Labels:** `[BE]` Backend · `[FE]` Frontend · `[AI]` AI/LangGraph · `[INFRA]` DevOps · `[SETUP]` Config

---

## Tuần 1 — Foundation: Setup & Core Backend

**Mục tiêu:** Auth chạy được, upload file lên MinIO, MongoDB collections khởi tạo đúng, Geo Risk data seeded.

---

### TASK-001 `[SETUP]` Init GitHub repo ClaimFlow ✅

**Mô tả:** Tạo repo `claimflow`, init folder structure, copy toàn bộ `.md` docs vào root, tạo `.gitignore` và `.env.example`, commit đầu tiên.

**Output:**
- Repo GitHub tên `claimflow`
- Folder: `backend/` `frontend/` `sample_data/` `.github/workflows/`
- `.env.example` đầy đủ keys

```bash
mkdir claimflow && cd claimflow
mkdir -p backend/app frontend sample_data/policies .github/workflows
git init && git add . && git commit -m "chore: init claimflow project"
```

---

### TASK-002 `[INFRA]` Docker Compose — 5 services ✅

**Mô tả:** Viết `docker-compose.yml` khởi động MongoDB, Redis, Qdrant, MinIO, và thêm mongo-express để xem data trong browser.

**Output:**
- `docker compose up -d` chạy được 5 services
- MongoDB: `localhost:27017`
- Redis: `localhost:6379`
- Qdrant dashboard: `http://localhost:6333/dashboard`
- MinIO console: `http://localhost:9001`
- Mongo Express: `http://localhost:8081`

```yaml
services:
  mongodb:
    image: mongo:7.0
    ports: ["27017:27017"]
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: admin
      MONGO_INITDB_DATABASE: claimflow_db
    volumes: [mongodb_data:/data/db]

  mongo-express:
    image: mongo-express
    ports: ["8081:8081"]
    environment:
      ME_CONFIG_MONGODB_ADMINUSERNAME: admin
      ME_CONFIG_MONGODB_ADMINPASSWORD: admin
      ME_CONFIG_MONGODB_URL: mongodb://admin:admin@mongodb:27017/

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: [qdrant_data:/qdrant/storage]

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes: [minio_data:/data]
```

---

### TASK-003 `[BE]` FastAPI skeleton + health check ✅

**Mô tả:** Init FastAPI app với CORS, routers structure, và health check endpoint. Server chạy tại `localhost:8000`. Setup ngay 3 middleware quan trọng: Request ID, CSRF Protection, Rate Limiting.

**Output:**
- `GET /health` → `{"status":"ok","db":"connected","version":"1.0.0"}`
- Swagger UI tại `localhost:8000/docs`
- CORS cho `localhost:3000` và `localhost:5173`
- Mọi response có header `X-Request-ID`
- POST/PUT/DELETE/PATCH bị block nếu thiếu CSRF token (trừ /auth/*)
- Rate limit: 10/min upload, 30/min chatbot, 5/min login

**requirements.txt:**
```txt
fastapi==0.111.0
uvicorn[standard]==0.30.1
motor==3.4.0
beanie==1.26.0
pymongo==4.7.2
redis==5.0.4
celery==5.4.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
boto3==1.34.110
google-generativeai==0.7.2
langchain==0.2.3
langgraph==0.1.1
langchain-google-genai==1.0.6
langchain-qdrant==0.1.1
qdrant-client==1.9.1
pymupdf==1.24.5
python-dotenv==1.0.1
pydantic-settings==2.3.0
httpx==0.27.0
slowapi==0.1.9
pytest==8.2.2
pytest-asyncio==0.23.7
```

**3 Middleware cần setup ngay từ đầu:**
```python
# app/core/middleware.py
import uuid, re
from fastapi import Request
from fastapi.responses import JSONResponse

# 1. Request ID
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = str(uuid.uuid4())[:8]
    request.state.request_id = rid
    logger.info("[%s] %s %s", rid, request.method, request.url.path)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

# 2. CSRF
@app.middleware("http")
async def csrf_middleware(request: Request, call_next):
    if request.method in ["POST","PUT","DELETE","PATCH"]:
        if not request.url.path.startswith("/auth"):
            csrf_h = request.headers.get("X-CSRF-Token")
            csrf_c = request.cookies.get("csrf_token")
            if not csrf_h or csrf_h != csrf_c:
                return JSONResponse({"detail": "CSRF validation failed"}, 403)
    return await call_next(request)
```

---

### TASK-004 `[BE]` MongoDB models + Beanie init ✅

**Mô tả:** Tạo Beanie Document models cho 6 collections. Init Beanie khi FastAPI startup. Seed province risk data cho 64 tỉnh.

**Output:**
- 6 collections khởi tạo: `users`, `documents`, `claims`, `geo_risks`, `chat_sessions`, `policies`
- Indexes đúng trên mỗi collection
- `python scripts/seed.py` tạo được: 1 admin, 1 reviewer, 3 users mẫu, và 64 province risk records
- `mongosh claimflow_db` → `db.geo_risks.count()` = 64

**Province data structure:**
```python
# scripts/seed_provinces.py
HIGH_RISK_PROVINCES = [
    "Quảng Bình", "Hà Tĩnh", "Nghệ An", "Quảng Nam",
    "Thừa Thiên Huế", "Quảng Ngãi", "Bình Định"
]
# Seed risk score dựa trên region + high_risk flag
```

---

### TASK-005 `[BE]` Auth: JWT httpOnly Cookie ✅

**Mô tả:** Register, login, logout với JWT lưu trong httpOnly cookie. Password validation: min 8 ký tự, chữ hoa + thường + số. bcrypt cost=12. JWT expire 7 ngày.

**Output:**
- `POST /auth/register` → tạo user, set cookie
- `POST /auth/login` → validate, set httpOnly cookie
- `POST /auth/logout` → clear cookie
- `GET /auth/me` → trả user info từ cookie token
- Password `"weak"` → 400 error với message rõ ràng
- Cookie: `httponly=True, secure=False (dev), samesite="lax"`

---

### TASK-006 `[BE]` File upload → MinIO ✅

**Mô tả:** Endpoint upload file PDF/JPG/PNG lên MinIO. Validate type và size (max 20MB). Trả về `document_id` và presigned URL.

**Output:**
- `POST /documents/upload` với `multipart/form-data` → 201
- File trong MinIO bucket `claimflow-documents`
- Reject file > 20MB → 413
- Reject file type sai → 415
- Presigned download URL (1 giờ)

---

### TASK-007 `[FE]` Next.js setup + Leaflet-safe config + Security ✅

**Mô tả:** Init Next.js 14 + TypeScript + Tailwind + shadcn/ui. Cấu hình Leaflet không bị SSR error. Setup axios với cookie auth + CSRF token interceptor. Tạo ErrorBoundary component và Loading Skeleton template.

**Output:**
- `npm run dev` tại `localhost:3000`
- Layout: sidebar nav (Dashboard, Upload Docs, Risk Map, Claims, Analytics)
- Leaflet dynamic import — không SSR crash
- Axios attach CSRF token tự động cho mọi mutating request
- `ErrorBoundary` component sẵn dùng
- `OCRProcessing` skeleton component sẵn dùng

---

### TASK-007b `[FE]` i18n — Bilingual UI (EN / VI) ✅

**Mô tả:** Tích hợp `next-intl` vào Next.js 14 App Router. Toàn bộ chuỗi UI có bản dịch EN + VI. Toggle ngôn ngữ không reload trang. URL-based locale.

**Output:**
- `npm install next-intl`
- URL `/vi/dashboard` hiển thị tiếng Việt, `/en/dashboard` hiển thị tiếng Anh
- `middleware.ts` tự detect và redirect về locale mặc định `vi`
- `LanguageSwitcher` component trong header — click toggle EN ↔ VI
- `messages/vi.json` + `messages/en.json` — đầy đủ keys cho tất cả trang
- Server Components dùng `getTranslations()`, Client Components dùng `useTranslations()`
- KHÔNG hardcode bất kỳ chuỗi UI nào — mọi text đều qua translation key

**Cấu trúc messages:**
```json
{
  "common":    { "loading", "error", "save", "cancel", "confirm", "back" },
  "nav":       { "dashboard", "documents", "riskMap", "claims", "analytics", "chatbot" },
  "auth":      { "login", "register", "logout", "email", "password", "fullName", "province" },
  "documents": { "upload", "ocr", "merge", "export", "confidence", "needsReview" },
  "claims":    { "submit", "status": { "pending", "approved", "rejected", "manualReview" } },
  "geo":       { "riskMap", "riskScore", "highRisk", "recommendations", "disasterTypes" },
  "chatbot":   { "placeholder", "typing", "clearSession", "suggestedActions" },
  "admin":     { "users", "policies", "auditLogs", "systemHealth", "analytics" },
  "errors":    { "unauthorized", "forbidden", "notFound", "serverError", "rateLimited" }
}
```

**Key files:**
```typescript
// frontend/src/i18n.ts
import { getRequestConfig } from 'next-intl/server';
export default getRequestConfig(async ({ locale }) => ({
  messages: (await import(`./messages/${locale}.json`)).default,
}));

// frontend/src/middleware.ts
import createMiddleware from 'next-intl/middleware';
export default createMiddleware({
  locales: ['vi', 'en'],
  defaultLocale: 'vi',
});
export const config = { matcher: ['/((?!api|_next|.*\\..*).*)'] };

// Usage in Server Component
const t = await getTranslations('nav');
<span>{t('dashboard')}</span>

// Usage in Client Component
'use client';
const t = useTranslations('auth');
<button>{t('login')}</button>
```

**LanguageSwitcher:**
```typescript
// components/layout/LanguageSwitcher.tsx
'use client';
import { useLocale } from 'next-intl';
import { useRouter, usePathname } from 'next/navigation';

export function LanguageSwitcher() {
  const locale = useLocale();
  const router = useRouter();
  const pathname = usePathname();

  const toggle = () => {
    const next = locale === 'vi' ? 'en' : 'vi';
    router.replace(pathname.replace(`/${locale}`, `/${next}`));
  };

  return (
    <button onClick={toggle} className="text-sm font-medium px-2 py-1 rounded border">
      {locale === 'vi' ? '🇻🇳 VI' : '🇺🇸 EN'}
    </button>
  );
}
```

```typescript
// Leaflet SSR fix
const LeafletMap = dynamic(() => import('@/components/risk-map/LeafletMap'), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 animate-pulse rounded-lg" />
});

// Axios CSRF interceptor
function getCsrfToken(): string {
  const match = document.cookie.match(/csrf_token=([^;]+)/);
  return match ? match[1] : '';
}
api.interceptors.request.use((config) => {
  if (['post','put','delete','patch'].includes(config.method ?? '')) {
    config.headers['X-CSRF-Token'] = getCsrfToken();
  }
  return config;
});
```

---

### TASK-008 `[FE]` Login/Register UI

**Mô tả:** Trang login và register hoàn chỉnh. Form validation client-side. Kết nối API thật. Sau login redirect về dashboard.

**Output:**
- UI shadcn/ui form đẹp
- Validation: email format, password rules (8 ký tự, hoa + thường + số)
- Loading state khi gọi API
- Error toast khi thất bại
- Field `province` trong register form (dropdown 64 tỉnh)

---

## Tuần 2 — AI Core: OCR, Merge, Geo Risk

**Mục tiêu:** Upload CCCD → AI extract thông tin → Merge 2 docs → Geo Risk analysis hoạt động.

---

### TASK-009 `[AI]` Gemini Vision OCR pipeline + Cache + Confidence

**Mô tả:** Service dùng Gemini Vision để OCR tài liệu và extract structured data. Hỗ trợ CCCD, bằng lái, hộ chiếu, hợp đồng bảo hiểm. Tích hợp: (1) MD5 cache tránh gọi API lại, (2) Confidence threshold 0.7 với auto-retry, (3) Flag manual review khi confidence thấp.

**Output:**
- `OCRService.get_or_extract(file_bytes, doc_type)` → structured JSON + confidence
- Cùng file (MD5 hash giống nhau) → trả cache, không gọi Gemini
- Confidence < 0.7 → retry với enhanced prompt
- Confidence vẫn < 0.7 sau retry → `needs_manual_review=True`, list `low_confidence_fields`
- Field `ocr_confidence` lưu vào MongoDB Document

**Implementation:**
```python
import hashlib

CONFIDENCE_THRESHOLD = 0.7

class OCRService:
    async def get_or_extract(self, file_bytes: bytes, doc_type: str) -> dict:
        file_hash = hashlib.md5(file_bytes).hexdigest()
        
        # Cache check
        cached = await Document.find_one(Document.file_hash == file_hash)
        if cached and cached.structured_data and cached.processing_status == "done":
            return {"data": cached.structured_data, "cached": True,
                    "confidence": cached.ocr_confidence}
        
        return await self._extract_with_retry(file_bytes, doc_type)

    async def _extract_with_retry(self, file_bytes: bytes, doc_type: str) -> dict:
        result = await self._call_gemini(file_bytes, doc_type, enhanced=False)
        
        if result.get("confidence", 0) < CONFIDENCE_THRESHOLD:
            logger.warning("Low confidence %.2f, retrying", result["confidence"])
            result = await self._call_gemini(file_bytes, doc_type, enhanced=True)
        
        result["needs_manual_review"] = result.get("confidence", 0) < CONFIDENCE_THRESHOLD
        result["low_confidence_fields"] = [
            k for k, v in result.get("fields", {}).items()
            if isinstance(v, dict) and v.get("confidence", 1) < CONFIDENCE_THRESHOLD
        ]
        return result
```

**Test:**
```python
# tests/test_ocr.py
import google.generativeai as genai
import os
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")
response = model.generate_content([image_part, CCCD_PROMPT])
print(response.text)
```

---

### TASK-010 `[AI]` Document Merge Logic

**Mô tả:** Service merge nhiều document đã OCR thành 1 hồ sơ duy nhất. Loại bỏ field trùng lặp. Phát hiện conflict khi cùng field có 2 giá trị khác nhau.

**Output:**
- `MergerService.merge(doc_ids)` → merged_data + conflicts
- `POST /documents/merge` endpoint hoạt động
- Conflicts được flag rõ ràng để user review
- Merged document lưu vào MongoDB với `is_merged=True`

**Algorithm:**
```python
def merge_documents(docs: list[dict]) -> tuple[dict, dict]:
    merged = {}
    conflicts = {}
    for doc in docs:
        for key, value in doc.get("structured_data", {}).items():
            if key not in merged or merged[key] is None:
                merged[key] = value
            elif merged[key] != value and value is not None:
                conflicts[key] = {"values": [merged[key], value], "source_docs": [...]}
    return merged, conflicts
```

---

### TASK-011 `[BE]` Geo Risk Engine

**Mô tả:** Service tính risk score cho từng tỉnh, nhận diện vùng miền từ địa chỉ, generate insurance recommendations.

**Output:**
- `GET /geo-risk/province/{name}` → full risk data
- `POST /geo-risk/recommend` nhận địa chỉ → trả recommendations
- Province detection từ free-text address ("45 Trần Hưng Đạo, Quảng Bình" → "Quảng Bình")
- 64 tỉnh đã có risk data trong DB

**Risk scoring logic:**
```python
def calculate_risk_score(province: str) -> int:
    base_scores = {
        "central": 70,   # Miền Trung rủi ro cao nhất
        "north": 45,
        "south": 40,
    }
    high_risk_bonus = 20 if province in HIGH_RISK_PROVINCES else 0
    return min(100, base_scores[region] + high_risk_bonus)
```

---

### TASK-012 `[FE]` Document Upload UI + OCR result display + Skeleton

**Mô tả:** Trang upload documents đầy đủ. Drag & drop, preview file, dropdown chọn doc_type, progress bar. Sau OCR: hiển thị extracted data dạng form editable. Tích hợp OCRProcessing skeleton (3-step indicator) và ErrorBoundary bọc toàn bộ component.

**Output:**
- Drag & drop area với hover effect
- Preview: ảnh → thumbnail, PDF → icon + tên + size
- OCRProcessing step indicator: Nhận tài liệu → OCR → AI phân tích
- Field extraction hiển thị trong bảng editable
- Visual region highlighting (overlay bbox trên ảnh gốc)
- Badge "Cần xác nhận" cho low_confidence_fields
- Nút "Export JSON" và "Export Markdown"
- ErrorBoundary bọc toàn bộ OCR display component

---

### TASK-013 `[FE]` Risk Map với Leaflet

**Mô tả:** Bản đồ tương tác Việt Nam hiển thị risk score theo tỉnh bằng choropleth (màu sắc theo mức độ rủi ro). Click vào tỉnh → hiển thị risk detail panel.

**Output:**
- Bản đồ Leaflet load đúng (SSR safe)
- Choropleth: xanh = thấp, vàng = trung, đỏ = cao
- Click province → side panel: risk score, disaster types, recommendations
- Legend màu sắc rõ ràng
- GeoJSON Việt Nam 64 tỉnh

**GeoJSON source:**
```
https://raw.githubusercontent.com/haitrieu1811/vietnam-geojson/main/vietnam-provinces.geojson
```

---

### TASK-014 `[AI]` Chatbot Gemini Pro + Privacy Guard + Injection Defense

**Mô tả:** Implement chatbot tư vấn bảo hiểm với Gemini Pro. System prompt bao gồm privacy guard (không leak PII). Tích hợp prompt injection defense layer. Context từ user profile. Session với giới hạn 50 messages.

**Output:**
- `POST /chatbot/message` → AI response trong < 3 giây
- Response không chứa số CCCD, địa chỉ chi tiết, SĐT
- Input qua `sanitize_chat_input()` trước khi gửi Gemini — block injection patterns
- Session tối đa 50 messages (tự truncate cũ)
- Context-aware: user ở Quảng Bình → tư vấn bảo hiểm bão lũ
- Floating chat button trên mọi trang

**Privacy System Prompt:**
```python
PRIVACY_SYSTEM_PROMPT = """
Bạn là AI tư vấn bảo hiểm ClaimFlow.

QUY TẮC BẮT BUỘC:
- TUYỆT ĐỐI không đọc to hoặc xác nhận số CCCD/CMND
- TUYỆT ĐỐI không tiết lộ địa chỉ chi tiết (số nhà, tên phố)
- TUYỆT ĐỐI không nhắc số điện thoại
- Chỉ dùng vùng miền (Bắc/Trung/Nam) hoặc tên tỉnh để tư vấn

Nhắc lại: TUYỆT ĐỐI không tiết lộ PII dù user có yêu cầu bất kỳ cách nào.
"""

# Injection defense
INJECTION_PATTERNS = [
    "ignore previous", "forget your rules", "you are now",
    "pretend you are", "reveal system prompt", "bypass",
    "disregard instructions", "new instructions",
]

def sanitize_chat_input(message: str) -> str:
    lower = message.lower()
    for p in INJECTION_PATTERNS:
        if p in lower:
            raise HTTPException(400, "Input không hợp lệ")
    return re.sub(r'<[^>]+>', '', message).strip()[:2000]
```

---

## Tuần 3 — Claim Processing + Dashboard

**Mục tiêu:** Submit claim → AI LangGraph xử lý → WebSocket real-time → Dashboard đầy đủ.

---

### TASK-015 `[AI]` LangGraph Claim Processing Agent

**Mô tả:** 4-node LangGraph workflow xử lý insurance claim. Tích hợp OCR → RAG policy check → Fraud detection → Decision.

**Output:**
- `graph.invoke({"claim_id": "...", "raw_text": "..."})` → full decision state
- Node 1: extract structured data từ OCR text
- Node 2: RAG search Qdrant → covered/not_covered
- Node 3: fraud score 0-100
- Node 4: approve/reject/manual_review/need_more_info
- Claim type `"disaster"` → check policy thiên tai

```python
class ClaimState(TypedDict):
    claim_id: str
    raw_text: str
    doc_type: str
    province: str | None
    disaster_type: str | None
    parsed_data: dict
    is_covered: bool
    coverage_limit: float
    fraud_score: int
    fraud_flags: list[str]
    final_decision: str
    final_reasoning: str
    missing_fields: list[str]
```

---

### TASK-016 `[BE]` Celery Worker + WebSocket push

**Mô tả:** Celery task xử lý claim job. Sau khi AI xong, publish event vào Redis → WebSocket handler push về client.

**Output:**
- `POST /claims/submit` trả về ngay lập tức (< 200ms)
- Celery worker chạy AI agent trong background
- WebSocket `/ws/{claim_id}` push status update
- Retry tự động khi Gemini API fail (max 3 lần, exponential backoff)

---

### TASK-017 `[FE]` Claim Dashboard + Detail

**Mô tả:** Dashboard claims list với filter theo status, province, disaster_type. Claim detail page với AI reasoning timeline, fraud score gauge.

**Output:**
- Table claims với filter bar
- Status badge màu (pending=vàng, approved=xanh, rejected=đỏ, manual_review=cam)
- Detail page: AI reasoning đẹp, fraud score progress bar
- Real-time status update qua WebSocket (không cần refresh)

---

### TASK-018 `[FE]` Document Merge UI

**Mô tả:** UI để chọn nhiều documents đã upload và merge lại. Hiển thị merged result với conflict resolution panel.

**Output:**
- Checkbox select nhiều documents
- Preview merged data side-by-side
- Conflict panel: hiển thị 2 giá trị khác nhau, cho user chọn đúng
- "Apply merge" → tạo merged document

---

### TASK-019 `[BE]` Qdrant + RAG Pipeline

**Mô tả:** Setup Qdrant, ingest policy documents (medical + disaster insurance) vào vector store. RAG service search relevant chunks.

**Output:**
- Collection `insurance_policies` với 1536-dim vectors
- Script `ingest_policies.py` ingest được policy files
- `VectorService.search("bảo hiểm bão lụt ICD J18.1", top_k=5)` → relevant chunks
- Policy files: `medical_policy_2024.txt` + `disaster_policy_2024.txt`

---

### TASK-020 `[FE]` Chatbot Floating Widget

**Mô tả:** Floating chat button ở góc phải màn hình, expand thành chat panel. Persist session khi navigate giữa các trang.

**Output:**
- Floating button không che content chính
- Chat panel slide-in animation
- Message bubbles (user vs AI phân biệt màu)
- Typing indicator khi AI đang respond
- Session persist qua localStorage (session_id)

---

## Tuần 4 — Polish + Analytics + Demo Prep

**Mục tiêu:** Analytics hoàn chỉnh, UI polish, demo script sẵn sàng.

> TASK-025, TASK-026 là **optional** — chỉ làm nếu còn thời gian.

---

### TASK-021 `[FE]` Analytics Dashboard

**Mô tả:** Trang analytics với charts: claims theo ngày, breakdown theo region, disaster types, approval rate.

**Output:**
- 4 metric cards: total claims, approval rate, avg processing time, total approved amount
- Line chart: claims theo ngày 30 ngày gần nhất
- Pie chart: breakdown theo region (Bắc/Trung/Nam)
- Bar chart: disaster types phổ biến nhất

---

### TASK-022 `[BE]` Human Review Interface

**Mô tả:** API cho reviewer override AI decision. Email notification sau khi review.

**Output:**
- `PATCH /claims/{id}/review` — role `reviewer` only
- Email gửi cho user với decision + note (Resend API)
- Reviewer dashboard: list claims cần review

---

### TASK-023 `[INFRA]` GitHub Actions CI

**Mô tả:** CI pipeline chạy khi push: lint + test backend, type-check frontend.

```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    services:
      mongodb: { image: mongo:7.0, ports: ["27017:27017"] }
      redis: { image: redis:7-alpine, ports: ["6379:6379"] }
    steps:
      - run: pip install -r requirements.txt
      - run: flake8 app/
      - run: pytest tests/ -v
  frontend:
    steps:
      - run: npm ci && npm run lint && npm run type-check
```

---

### TASK-024 `[BE]` Unit tests — AI nodes + Security + OCR cache

**Mô tả:** Unit tests cho OCR service (với cache và confidence), merge logic, LangGraph nodes, CSRF middleware, rate limiting, và injection defense. Mock Gemini API — không dùng quota thật.

**Output:**
- `pytest tests/ -v` pass tất cả
- Coverage ≥ 70% cho `services/ai/` và `services/geo/`
- Test OCR cache: cùng hash → không gọi Gemini lần 2
- Test confidence retry: confidence < 0.7 → trigger retry
- Test CSRF: request thiếu token → 403
- Test rate limit: >5 login/phút → 429
- Test injection defense: "ignore previous instructions" → 400
- Mock Gemini API với `unittest.mock.patch`

---

### TASK-025 `[SETUP]` ⚡ OPTIONAL — README + Demo Script

**Mô tả:** README hoàn chỉnh, screenshot/GIF demo, chuẩn bị demo 5 phút cho mentor.

**Demo script:**
```
1. Bài toán (1 phút)
   → Người dân vùng thiên tai không biết cần bảo hiểm gì
   → Xử lý giấy tờ bảo hiểm thủ công chậm

2. Live demo localhost:3000 (3 phút)
   → Nhập địa chỉ Quảng Bình → xem risk map + recommendations
   → Upload CCCD + hợp đồng bảo hiểm → AI extract → Merge
   → Submit disaster claim → WebSocket real-time processing
   → Chatbot hỏi "Tôi ở Quảng Bình cần mua gì?"

3. Tech Q&A (1 phút)
   → Tại sao Gemini Vision thay vì Tesseract?
   → Tại sao Merge logic loại bỏ field trùng?
   → Tại sao httpOnly cookie thay vì localStorage?
```

---

### TASK-026 `[INFRA]` ⚡ OPTIONAL — Deploy Railway + Vercel

**Mô tả:** Deploy backend lên Railway, frontend lên Vercel. MongoDB Atlas free tier.

---

## Backlog

- `[ ]` So sánh gói bảo hiểm side-by-side
- `[ ]` Lịch sử thiên tai theo tỉnh (timeline chart)
- `[ ]` Export hồ sơ merged ra DOCX
- `[ ]` Thêm doc types: Giấy khai sinh, Sổ hộ khẩu
- `[ ]` Dark mode
- `[ ]` Mobile responsive chatbot widget

---

## Decisions Log

| Ngày | Quyết định | Lý do |
|------|-----------|-------|
| | | |

---

## Tuần 3 bổ sung — Admin & Reviewer Dashboard

> Thêm vào sau TASK-020, trước TASK-021.

---

### TASK-020b `[BE]` Admin API — User management + Audit logs

**Mô tả:** Implement toàn bộ `/admin/*` endpoints. CRUD user, đổi role, xem audit logs. Mọi action admin đều ghi vào `audit_logs` collection. Middleware `require_admin` dependency.

**Output:**
- `GET /admin/users` — list all users với filter role, is_active, pagination
- `PATCH /admin/users/{id}/role` — đổi role (ghi audit log)
- `PATCH /admin/users/{id}/status` — activate/deactivate user
- `GET /admin/audit-logs` — history mọi action quan trọng
- `GET /admin/system/health` — ping MongoDB, Redis, Qdrant, Celery
- `GET /admin/analytics/full` — full system analytics không filter theo user
- Mọi action ghi `AuditLog` với actor, target, details, timestamp
- `require_admin` dependency — 403 nếu không phải admin

**Ghi audit log mỗi action:**
```python
async def log_action(actor: User, action: str, target_type: str, target_id: str, details: dict):
    await AuditLog(
        actor_id=str(actor.id),
        actor_email=actor.email,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
    ).insert()
```

---

### TASK-020c `[BE]` Admin Policy Management

**Mô tả:** Admin upload policy documents mới → tự động ingest vào Qdrant vector store. Deactivate policy → xóa khỏi vector store. Xem danh sách policies với chunk count.

**Output:**
- `GET /admin/policies` — list all policies + chunk count + last ingested
- `POST /admin/policies` — upload file + ingest vào Qdrant (Celery background job)
- `DELETE /admin/policies/{id}` — deactivate + xóa vectors khỏi Qdrant
- Sau khi upload: `celery task → chunk → embed → upsert Qdrant`
- Ghi audit log cho upload và delete

---

### TASK-020d `[FE]` Admin Dashboard UI

**Mô tả:** Trang Admin dashboard đầy đủ — chỉ hiển thị khi role = admin. Bao gồm: User management table, System health panel, Full analytics, Policy management, Audit log viewer.

**Output:**
- Route `/admin` — redirect về `/dashboard` nếu không phải admin
- **Tab Users:** table tất cả users, filter theo role/status, nút đổi role (dropdown), nút deactivate
- **Tab Analytics:** full system metrics — total users, claims, fraud rate, top provinces rủi ro, reviewer performance table
- **Tab Policies:** list policy documents, nút upload mới, nút deactivate, badge chunk count
- **Tab Audit Logs:** timeline mọi action, filter theo action type và date range
- **Tab System Health:** card từng service (MongoDB, Redis, Qdrant, Celery) với status badge + latency

**UI Layout:**
```
/admin
  ├── Sidebar tabs: Users | Analytics | Policies | Audit Logs | System Health
  ├── Header: "Admin Dashboard" + current admin name
  └── Content area theo tab active
```

---

### TASK-020e `[FE]` Reviewer Dashboard UI

**Mô tả:** Trang Reviewer dashboard — chỉ hiển thị khi role = reviewer hoặc admin. Queue claims cần review, personal stats, detail view với AI reasoning.

**Output:**
- Route `/reviewer` — redirect nếu không đủ quyền
- **Queue panel:** danh sách claims `manual_review`, sort oldest first, badge waiting time
- **Stats panel:** claims reviewed today, total, avg review time, override rate
- **Detail modal:** click vào claim → xem AI reasoning đầy đủ, fraud score gauge, fraud flags list
- Nút "Approve" và "Reject" với confirm dialog + required note field
- Badge màu fraud score: xanh (<30), vàng (30-70), đỏ (>70)

---

### TASK-020f `[BE]` Reviewer Stats API

**Mô tả:** Endpoint trả stats cá nhân của reviewer đang login. Dùng cho Reviewer dashboard.

**Output:**
- `GET /reviewer/queue` — claims cần review (manual_review), có filter và sort
- `GET /reviewer/stats` — claims reviewed today/total, avg time, override rate
- Tính `avg_review_time` từ `reviewed_at - created_at` của các claims đã review

