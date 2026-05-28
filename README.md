# ClaimFlow 🌊

> Nền tảng bảo hiểm thông minh — Xử lý tài liệu AI, phân tích rủi ro thiên tai, và tư vấn bảo hiểm cá nhân hóa cho thị trường Việt Nam.

---

## Giới thiệu

ClaimFlow là ứng dụng insurtech tích hợp AI giúp người dùng Việt Nam hiểu rõ rủi ro thiên tai tại địa phương, xử lý tài liệu bảo hiểm tự động, và nhận tư vấn gói bảo hiểm phù hợp — tất cả trong một nền tảng duy nhất.

Dự án được xây dựng trong context của CoverGo (insurtech), tích hợp các khái niệm System Design thực tế: LangGraph agent, RAG pipeline, event-driven architecture, message queue, WebSocket, và containerization.

---

## Tính năng chính

### 📄 Document Intelligence
- Upload nhiều tài liệu: CCCD, hợp đồng bảo hiểm, bằng lái xe, hộ chiếu, giấy đăng ký xe
- OCR tiếng Việt chính xác cao với Gemini Vision API
- Trích xuất dữ liệu có cấu trúc từ PDF/PNG/JPG/JPEG
- **Merge nhiều tài liệu** — loại bỏ field trùng lặp, hợp nhất thành 1 hồ sơ
- Visual region highlighting — đánh dấu vùng đã trích xuất
- Chỉnh sửa dữ liệu qua giao diện trực quan
- Export JSON và Markdown

### 🌍 Geo Risk Intelligence
- Nhận diện vùng miền từ địa chỉ (23 tỉnh Bắc / 19 tỉnh Trung / 22 tỉnh Nam)
- Risk score theo tỉnh/vùng dựa trên dữ liệu thiên tai lịch sử
- Phát hiện tỉnh rủi ro cao: Quảng Bình, Hà Tĩnh, Nghệ An, Quảng Nam...
- Cảnh báo thiên tai: Bão, Lũ lụt, Ngập úng, Sạt lở
- Bản đồ tương tác hiển thị vùng rủi ro (Leaflet)
- Đề xuất gói bảo hiểm phù hợp theo rủi ro địa lý

### 💬 AI Insurance Chatbot
- Powered by Google Gemini Pro
- Tư vấn bảo hiểm 24/7 — cá nhân hóa theo nhu cầu
- Giải thích thuật ngữ bảo hiểm bằng ngôn ngữ đơn giản
- Tư vấn theo vùng miền (Bắc/Trung/Nam)
- Cross-sell gợi ý combo: Nhân thọ + Sức khỏe + Thiên tai
- Bảo vệ thông tin nhạy cảm — không tiết lộ CCCD, địa chỉ chi tiết, SĐT
- Floating widget tiện lợi trên mọi trang

### 🔍 Claim Processing (AI Agent)
- LangGraph 4-node workflow: `document_parser` → `policy_checker` → `fraud_detector` → `decision_maker`
- RAG search trong policy documents
- Real-time status update qua WebSocket
- Human review interface cho reviewer
- Analytics dashboard

### 🌐 Bilingual UI (EN / VI)
- Toàn bộ giao diện hỗ trợ 2 ngôn ngữ: Tiếng Việt (mặc định) và English
- Chuyển ngôn ngữ tức thì — không reload trang
- URL-based locale: `/vi/dashboard` · `/en/dashboard`
- Powered by **next-intl** (Next.js 14 App Router native)
- Tất cả labels, messages, error texts đều có bản dịch đầy đủ

---

## Tech Stack

### Frontend
| Công nghệ | Mục đích |
|---|---|
| Next.js 14 (App Router) | Framework React SSR/SSG |
| TypeScript | Type safety |
| Tailwind CSS + shadcn/ui | Styling + Component library |
| Leaflet + React Leaflet | Bản đồ tương tác rủi ro thiên tai |
| Recharts | Analytics charts |
| WebSocket API | Real-time claim status |
| next-intl | Bilingual UI — EN / VI (URL-based locale) |

### Backend
| Công nghệ | Mục đích |
|---|---|
| FastAPI | REST API async, tự gen OpenAPI docs |
| Beanie + Motor | Async ODM cho MongoDB |
| Celery + Redis | Async task queue + Message broker |
| slowapi | Rate limiting per endpoint per IP |
| JWT (HS256) | Authentication — 7 ngày expire, httpOnly cookie |
| bcrypt (cost 12) | Password hashing |
| Pydantic | Input validation + schemas |

### AI Layer
| Công nghệ | Mục đích |
|---|---|
| Google Gemini Vision | OCR tiếng Việt + Document parsing |
| Google Gemini Pro | LLM chatbot + RAG reasoning |
| Google text-embedding-004 | Embedding cho vector search |
| LangGraph | Orchestrate AI agent workflow |
| LangChain | RAG pipeline, tool integration |
| Qdrant | Vector database cho RAG |
| PyMuPDF | Extract text từ PDF nhiều trang |

### Infrastructure
| Công nghệ | Mục đích |
|---|---|
| MongoDB 7.0 | Primary database (document store) |
| Redis | Cache + Celery broker + Pub/Sub |
| MinIO (dev) / AWS S3 (prod) | File storage |
| Docker Compose | Development environment |
| GitHub Actions | CI/CD pipeline |

---

## Kiến trúc hệ thống

```
┌──────────────────────────────────────────────────────────┐
│                      Client Layer                        │
│    Next.js 14 — React + TypeScript + Tailwind + Leaflet  │
└───────────────────────┬──────────────────────────────────┘
                        │ HTTP REST + WebSocket
┌───────────────────────▼──────────────────────────────────┐
│                API Gateway + Auth                        │
│      FastAPI — JWT · Rate Limiting · CORS · Routing      │
└──────┬──────────────┬───────────────┬────────────────────┘
       │              │               │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────────┐
│  Document   │ │  Geo Risk  │ │   Chatbot      │
│  Service    │ │  Service   │ │   Service      │
│             │ │            │ │                │
│ OCR·Merge   │ │ Province   │ │ Gemini Pro     │
│ Gemini      │ │ Risk Score │ │ RAG · Memory   │
│ Vision      │ │ Map data   │ │ Privacy guard  │
└──────┬──────┘ └─────┬──────┘ └─────┬──────────┘
       │              │               │
┌──────▼──────────────▼───────────────▼──────────┐
│          Message Queue (Redis + Celery)         │
│   Document jobs · AI inference · Notifications  │
└──────┬──────────────┬───────────────┬───────────┘
       │              │               │
┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  MongoDB    │ │   Qdrant   │ │  MinIO/S3  │
│             │ │            │ │            │
│ Users·Docs  │ │ Policy RAG │ │ PDF·Images │
│ Claims·Risk │ │ Vectors    │ │ Documents  │
└─────────────┘ └────────────┘ └────────────┘
```

### AI Agent Flow (Claim Processing)

```
Upload tài liệu
      │
      ▼
[Node 1] document_parser
  Gemini Vision OCR → extract structured data
  Merge nhiều docs → loại bỏ field trùng
      │
      ▼
[Node 2] policy_checker
  RAG search Qdrant → kiểm tra điều khoản
  Covered? Coverage limit?
      │
      ▼
[Node 3] fraud_detector
  Amount anomaly? Duplicate claim? Whitelist hospital?
  Fraud score: 0–100
      │
      ▼
[Node 4] decision_maker
  score < 30 + covered   → APPROVE
  not covered            → REJECT + reason
  score > 70             → MANUAL REVIEW
  thiếu thông tin        → LOOP về node 1
      │
      ▼
  WebSocket push → Client real-time
```

### Geo Intelligence Flow

```
User nhập địa chỉ
      │
      ▼
Geo Service nhận diện tỉnh/vùng miền
      │
      ▼
Risk Score Engine
  ├── Dữ liệu thiên tai lịch sử
  ├── Phân loại rủi ro: Bão / Lũ / Sạt lở / Ngập úng
  └── Score theo tỉnh (0–100)
      │
      ▼
Insurance Recommendation AI
  ├── 95% risk → Bảo hiểm bão bắt buộc
  ├── 90% risk → Bảo hiểm ngập nước
  └── Combo suggestion: Nhân thọ + Sức khỏe + Thiên tai
      │
      ▼
Hiển thị bản đồ Leaflet + Báo cáo rủi ro
```

---

## Cấu trúc thư mục

```
claimflow/
├── backend/
│   └── app/
│       ├── api/routes/
│       │   ├── auth.py
│       │   ├── documents.py       # Upload, OCR, merge
│       │   ├── geo_risk.py        # Province risk analysis
│       │   ├── chatbot.py         # AI chatbot endpoint
│       │   ├── claims.py          # Claim processing
│       │   ├── analytics.py
│       │   ├── reviewer.py
│       │   └── admin.py
│       ├── core/
│       │   ├── config.py
│       │   ├── security.py        # JWT + bcrypt
│       │   ├── database.py        # MongoDB + Beanie init
│       │   ├── middleware.py      # Request ID + CSRF
│       │   └── rate_limit.py      # slowapi setup
│       ├── models/
│       │   ├── user.py
│       │   ├── document.py        # OCR document model
│       │   ├── claim.py
│       │   ├── geo_risk.py        # Province risk data
│       │   ├── chat_session.py
│       │   ├── policy.py
│       │   └── audit_log.py
│       ├── schemas/
│       ├── services/
│       │   ├── ai/
│       │   │   ├── agent.py       # LangGraph workflow
│       │   │   ├── nodes.py       # 4 agent nodes
│       │   │   ├── rag.py         # RAG pipeline
│       │   │   ├── ocr.py         # Gemini Vision OCR
│       │   │   ├── merger.py      # Document merge logic
│       │   │   └── chatbot.py     # Gemini Pro chatbot
│       │   ├── geo/
│       │   │   ├── province_data.py  # Static risk data 63 tỉnh
│       │   │   └── risk_engine.py    # Risk scoring logic
│       │   ├── province_mapper.py    # province → region lookup
│       │   ├── storage.py
│       │   └── notification.py
│       ├── tasks/
│       │   └── document_processor.py
│       └── main.py
├── frontend/
│   └── src/
│       ├── app/
│       │   └── [locale]/          # next-intl locale segment
│       │       ├── (auth)/login · register
│       │       ├── dashboard/     # Claim list + status
│       │       ├── documents/     # Upload + OCR UI
│       │       ├── risk-map/      # Leaflet risk map
│       │       ├── claims/[id]/   # Claim detail
│       │       ├── analytics/
│       │       ├── admin/
│       │       └── reviewer/
│       ├── components/
│       │   ├── documents/         # Upload, merge, highlight
│       │   ├── risk-map/          # Map + risk badge
│       │   ├── chatbot/           # Floating widget
│       │   ├── layout/
│       │   │   └── LanguageSwitcher.tsx   # EN ↔ VI toggle
│       │   └── ui/                # shadcn components
│       ├── messages/
│       │   ├── vi.json            # Vietnamese strings (default)
│       │   └── en.json            # English strings
│       ├── i18n.ts                # next-intl config
│       ├── middleware.ts          # locale detection + routing
│       ├── lib/
│       │   ├── api.ts
│       │   └── websocket.ts
│       └── types/
├── sample_data/
│   ├── policies/                  # Policy docs cho RAG
│   ├── province_risk.json         # Risk data 63 tỉnh
│   └── generate_sample_pdfs.py
├── docker-compose.yml
├── .env.example
├── CLAUDE.md
├── README.md
├── TASKS.md
├── SCHEMA.md
├── ARCHITECTURE.md
├── CONVENTIONS.md
├── API.md
└── ERRORS.md
```

---

## Phân quyền (Authorization)

ClaimFlow có 3 roles với quyền hạn khác nhau:

| Role | Truy cập |
|------|---------|
| **User** | Tài liệu, claims của mình, chatbot, bản đồ rủi ro |
| **Reviewer** | Tất cả claims, xét duyệt thủ công, reviewer dashboard |
| **Admin** | Tất cả + quản lý users, policy documents, audit logs, system health |

### Admin Dashboard (`/admin`)
- **Users tab:** Xem và quản lý tất cả users, đổi role, activate/deactivate
- **Analytics tab:** Full system metrics — total users, claims, fraud rate, reviewer performance
- **Policies tab:** Upload policy documents mới cho RAG, deactivate policy cũ
- **Audit Logs tab:** Timeline mọi action quan trọng trong hệ thống
- **System Health tab:** Status realtime của MongoDB, Redis, Qdrant, Celery, Gemini API quota

### Reviewer Dashboard (`/reviewer`)
- Queue claims cần xét duyệt thủ công (fraud score cao)
- Xem AI reasoning đầy đủ + fraud flags
- Approve hoặc Reject với note bắt buộc
- Personal stats: số claims đã review, avg review time, override rate

---

## Bảo mật

### Authentication
- JWT HS256, expire 7 ngày (10080 phút)
- Password: bcrypt cost factor 12, min 8 ký tự, phải có chữ hoa + chữ thường + số
- Token lưu **httpOnly cookie** (không localStorage — tránh XSS)

### CSRF Protection
httpOnly cookie ngăn XSS nhưng tạo CSRF vulnerability. Giải pháp Double Submit Cookie:
- Login set 2 cookie: `access_token` (httpOnly) + `csrf_token` (non-httpOnly)
- Frontend đọc `csrf_token` và attach vào header `X-CSRF-Token`
- Middleware verify header == cookie trước mọi mutating request

### CORS Policy
```
Allowed Origins: http://localhost:3000, http://localhost:5173, production URL
Methods: GET, POST, PUT, DELETE, PATCH
Headers: Content-Type, Authorization, X-CSRF-Token
Credentials: true
```

### Rate Limiting (per IP)
```
POST /auth/login        → 5/phút   (chống brute force)
POST /documents/upload  → 10/phút  (OCR nặng)
POST /chatbot/message   → 30/phút  (chat bình thường)
```

### Data Protection
- Không tiết lộ CCCD, địa chỉ chi tiết, SĐT trong chatbot response
- Prompt injection defense — block "ignore previous instructions" và tương tự
- Chỉ dùng vùng miền (Bắc/Trung/Nam) để tư vấn
- Input validation toàn bộ qua Pydantic schemas + sanitize function
- Request ID header (`X-Request-ID`) cho mọi response — trace bug dễ hơn

### OCR Privacy
- File hash (MD5) cache OCR results — cùng file không gọi Gemini API 2 lần
- Confidence threshold 0.7 — field dưới ngưỡng được flag "Cần xác nhận"
- Không lưu raw image vào DB — chỉ lưu extracted text và S3 key

---

## Cài đặt & Chạy local

### Yêu cầu
- Docker Desktop, Python 3.11+, Node.js 18+

### 1. Clone và cấu hình
```bash
git clone https://github.com/your-username/claimflow.git
cd claimflow
cp .env.example .env
# Điền GEMINI_API_KEY vào .env
```

### 2. Chạy với Docker Compose
```bash
docker compose up -d
cd backend && python scripts/seed.py
cd backend && python scripts/ingest_policies.py
```

### 3. Chạy riêng lẻ
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
celery -A app.tasks worker --loglevel=info

# Frontend
cd frontend && npm install && npm run dev
```

### Truy cập
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Qdrant: http://localhost:6333/dashboard
- MinIO: http://localhost:9001

---

## Environment Variables

```env
GEMINI_API_KEY=AIza...
MONGODB_URL=mongodb://admin:admin@localhost:27017
MONGODB_DB_NAME=claimflow_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=10080
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_BUCKET_NAME=claimflow-documents
S3_ENDPOINT_URL=http://localhost:9000
QDRANT_URL=http://localhost:6333
RESEND_API_KEY=re_...
```

---

## System Design Concepts Áp dụng

| Concept | Áp dụng trong ClaimFlow |
|---|---|
| Message Queue | Redis + Celery xử lý OCR job async |
| Pub/Sub | Redis Pub/Sub → WebSocket push real-time |
| Event-Driven | Submit doc → event → worker → AI → notify |
| RAG | Qdrant vector search policy cho claim check |
| LangGraph Agent | 4-node stateful workflow, conditional routing, auto-retry |
| API Gateway | FastAPI: auth + rate limit + CSRF + routing tập trung |
| Embedded Documents | DocumentEmbed trong Claim, ChatMessage trong Session |
| Database Indexing | Index user_id, status, province, file_hash, created_at |
| Containerization | Docker Compose 5 services |
| CQRS (nhẹ) | Write: Celery worker / Read: API GET tách biệt |
| Geo Intelligence | Province risk scoring + Leaflet map visualization |
| Data Privacy | PII protection, prompt injection defense, CSRF protection |
| Caching | OCR result cache bằng MD5 file hash |
| Rate Limiting | slowapi per endpoint per IP |
| Distributed Tracing | Request ID header trên mọi response |

---

## Tác giả

**Hồ Duy Vũ** — AI Engineer Intern @ CoverGo
vu.hoduy@covergo.com

---

## License

MIT License
