# API.md — API Reference

> Request/response format đầy đủ. Claude đọc khi viết code FE gọi API hoặc viết endpoint mới.
> Cập nhật: bao gồm security headers, CSRF, rate limit, confidence fields, edit history.

---

## Base URL & Auth

```
Development: http://localhost:8000
Production:  https://claimflow-backend.railway.app
```

**Auth:** JWT trong **httpOnly cookie** — browser tự attach, không cần code thêm.

**CSRF:** Mọi `POST/PUT/DELETE/PATCH` phải kèm header `X-CSRF-Token` (lấy từ cookie `csrf_token` non-httpOnly).

**Response headers chuẩn:**
```
X-Request-ID: a3f8b2c1     ← trace bug theo request
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1716000000
```

---

## Error Codes

| Code | Ý nghĩa | Ví dụ |
|------|---------|-------|
| 400 | Bad request / validation error | Email sai format, password yếu |
| 401 | Chưa đăng nhập / token hết hạn | Cookie không có hoặc expired |
| 403 | Không đủ quyền hoặc CSRF fail | User thường vào reviewer endpoint, thiếu X-CSRF-Token |
| 404 | Resource không tồn tại | Document ID không tìm thấy |
| 409 | Conflict / duplicate | Email đã đăng ký |
| 413 | File quá lớn | Upload > 20MB |
| 415 | File type không hỗ trợ | Upload .docx |
| 422 | Pydantic validation fail | FastAPI tự handle |
| 429 | Rate limit exceeded | Quá 5 login/phút |
| 500 | Server error | Unexpected exception |

**Error response format:**
```json
{ "detail": "Human-readable error message" }
```

---

## Auth

### POST `/auth/register`
```json
// Request
{
  "email": "user@example.com",
  "password": "StrongPass123!",
  "full_name": "Nguyễn Văn A",
  "province": "Quảng Bình"
}

// Response 201
{
  "id": "...",
  "email": "user@example.com",
  "full_name": "Nguyễn Văn A",
  "role": "user",
  "province": "Quảng Bình",
  "region": "central"
}
// Errors: 400 (email exists), 400 (password weak), 422 (validation)
```

### POST `/auth/login`
```json
// Request
{ "email": "user@example.com", "password": "StrongPass123!" }

// Response 200 — set 2 httpOnly+non-httpOnly cookies
{
  "message": "Login successful",
  "user": { "id": "...", "email": "...", "role": "user", "province": "Quảng Bình" }
}
// Rate limit: 5/phút per IP → 429 nếu vượt
// Error 401: sai email/password
```

### POST `/auth/logout`
```json
// Response 200 — clear cookies
{ "message": "Logged out" }
```

### GET `/auth/me`
```json
// Response 200
{
  "id": "...",
  "email": "...",
  "full_name": "...",
  "role": "user",
  "province": "Quảng Bình",
  "region": "central",
  "is_active": true
}
```

---

## Documents

### POST `/documents/upload`
`multipart/form-data` — Rate limit: **10/phút per IP**

```
file:      [binary]   PDF/PNG/JPG/JPEG — max 20MB
doc_type:  "cccd"     cccd|cmnd|driver_license|passport|vehicle_registration|insurance_policy|other
```

```json
// Response 201
{
  "document_id": "...",
  "file_name": "cccd_front.jpg",
  "file_hash": "a3f8b2c1d4e5f6...",
  "doc_type": "cccd",
  "processing_status": "pending",
  "message": "Uploaded. OCR processing started.",
  "cached": false
}
// cached=true nếu file hash đã OCR trước đó → trả ngay không queue Celery
```

### GET `/documents/{id}`
```json
// Response 200
{
  "id": "...",
  "doc_type": "cccd",
  "file_name": "cccd_front.jpg",
  "file_hash": "a3f8b2c1...",
  "file_size_kb": 245,
  "processing_status": "done",

  "ocr_confidence": 0.94,
  "needs_manual_review": false,
  "low_confidence_fields": [],

  "structured_data": {
    "id_number": "001234567890",
    "full_name": "NGUYỄN VĂN AN",
    "date_of_birth": "15/03/1990",
    "sex": "Nam",
    "place_of_origin": "Hà Nội",
    "place_of_residence": "45 Trần Hưng Đạo, Hà Nội",
    "expiry_date": "15/03/2035"
  },
  "extracted_fields": [
    {
      "key": "id_number",
      "value": "001234567890",
      "confidence": 0.98,
      "bbox": [120, 45, 280, 30]
    },
    {
      "key": "place_of_residence",
      "value": "45 Trần Hưng Đạo, Hà Nội",
      "confidence": 0.62,
      "bbox": [80, 180, 400, 25]
    }
  ],

  "version": 2,
  "edit_history": [
    {
      "field": "place_of_residence",
      "old_value": "45 Trần Hưng Đao, Hà Nội",
      "new_value": "45 Trần Hưng Đạo, Hà Nội",
      "edited_by": "user-id-...",
      "timestamp": "2024-05-15T11:00:00Z"
    }
  ],

  "is_merged": false,
  "merged_from": [],

  "download_url": "https://presigned-s3-url...",
  "created_at": "...",
  "updated_at": "..."
}

// Khi needs_manual_review = true:
{
  "needs_manual_review": true,
  "low_confidence_fields": ["place_of_residence", "expiry_date"],
  "ocr_confidence": 0.58
}
```

### POST `/documents/merge`
```json
// Request
{ "document_ids": ["id1", "id2", "id3"] }

// Response 200
{
  "merged_document_id": "...",
  "merged_data": {
    "id_number": "001234567890",
    "full_name": "NGUYỄN VĂN AN",
    "policy_number": "BH-2024-001234",
    "insurance_type": "Nhân thọ"
  },
  "conflicts": {
    "date_of_birth": {
      "values": ["15/03/1990", "1990-03-15"],
      "source_docs": ["id1", "id2"]
    }
  },
  "stats": {
    "total_fields": 12,
    "merged_clean": 10,
    "conflicts": 2
  }
}
```

### PUT `/documents/{id}/fields`
Yêu cầu `X-CSRF-Token` header.
```json
// Request
{
  "field_updates": {
    "place_of_residence": "45 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội"
  }
}

// Response 200
{
  "id": "...",
  "structured_data": { "...updated..." },
  "version": 3,
  "edit_history": ["..."]
}
```

### GET `/documents/{id}/export`
```
// Query: ?format=json hoặc ?format=markdown
// Response: file download với Content-Disposition header
```

---

## Geo Risk

### GET `/geo-risk/province/{province_name}`
```json
// Response 200
{
  "province_name": "Quảng Bình",
  "province_code": "QB",
  "region": "central",
  "overall_risk_score": 92,
  "is_high_risk": true,
  "risk_factors": ["typhoon_path", "flood_prone", "mountainous"],
  "disaster_risks": [
    { "type": "storm", "risk_score": 95, "frequency": "high", "historical_events": 47 },
    { "type": "flood", "risk_score": 90, "frequency": "high", "historical_events": 38 },
    { "type": "landslide", "risk_score": 75, "frequency": "medium", "historical_events": 12 }
  ],
  "recommendations": [
    {
      "insurance_type": "Bảo hiểm bão lũ",
      "priority_score": 95,
      "reason": "Nằm trực tiếp trên đường đi của bão Tây Bắc Thái Bình Dương",
      "estimated_premium": "2,000,000 - 5,000,000 VND/năm"
    },
    {
      "insurance_type": "Bảo hiểm nhà ở",
      "priority_score": 88,
      "reason": "Nguy cơ ngập lụt và sạt lở đất cao",
      "estimated_premium": "1,500,000 - 3,000,000 VND/năm"
    }
  ]
}
```

### GET `/geo-risk/map`
```json
// Response 200 — dùng cho Leaflet choropleth (simplified, < 500KB)
{
  "provinces": [
    {
      "name": "Quảng Bình", "code": "QB",
      "lat": 17.47, "lng": 106.62,
      "risk_score": 92, "is_high_risk": true,
      "region": "central",
      "top_risk": "storm"
    },
    {
      "name": "Hà Nội", "code": "HN",
      "lat": 21.02, "lng": 105.84,
      "risk_score": 35, "is_high_risk": false,
      "region": "north",
      "top_risk": "flood"
    }
  ],
  "summary": {
    "high_risk_count": 12,
    "medium_risk_count": 28,
    "low_risk_count": 24
  }
}
```

### POST `/geo-risk/recommend`
Yêu cầu `X-CSRF-Token` header.
```json
// Request
{ "address": "45 Trần Hưng Đạo, Quảng Bình" }

// Response 200
{
  "detected_province": "Quảng Bình",
  "detected_region": "central",
  "risk_level": "HIGH",
  "overall_score": 92,
  "recommendations": [
    {
      "insurance_type": "Bảo hiểm bão lũ",
      "priority_score": 95,
      "reason": "Quảng Bình nằm trên đường đi của bão",
      "estimated_premium": "2,000,000 - 5,000,000 VND/năm"
    }
  ],
  "combo_suggestion": {
    "packages": ["Nhân thọ", "Sức khỏe", "Thiên tai"],
    "discount": "15% khi mua combo 3 gói",
    "reason": "Bảo vệ toàn diện cho vùng rủi ro cao"
  }
}
```

---

## Chatbot

Rate limit: **30/phút per IP**

### POST `/chatbot/message`
Yêu cầu `X-CSRF-Token` header.
```json
// Request
{
  "message": "Tôi ở Quảng Bình, cần mua bảo hiểm gì?",
  "session_id": "optional-existing-session-id"
}

// Response 200
{
  "session_id": "...",
  "response": "Vì bạn ở vùng Bắc Trung Bộ — khu vực có rủi ro bão lũ cao, tôi khuyên...",
  "suggested_actions": [
    { "label": "Xem bản đồ rủi ro", "action": "navigate", "path": "/risk-map" },
    { "label": "Xem gói bảo hiểm bão lũ", "action": "navigate", "path": "/compare" }
  ]
}

// Error 400: input chứa injection patterns
{ "detail": "Input không hợp lệ" }

// Error 429: vượt rate limit
{ "detail": "Rate limit exceeded. Retry after 60 seconds." }
```

### GET `/chatbot/session/{session_id}`
```json
// Response 200
{
  "session_id": "...",
  "message_count": 12,
  "messages": [
    { "role": "user", "content": "...", "timestamp": "..." },
    { "role": "assistant", "content": "...", "timestamp": "..." }
  ]
}
// Lưu ý: chỉ trả 50 messages gần nhất — tránh response quá lớn
```

### DELETE `/chatbot/session/{session_id}`
```json
// Response 200
{ "message": "Session cleared" }
```

---

## Claims

### POST `/claims/submit`
`multipart/form-data` — Yêu cầu `X-CSRF-Token` header.

```
claim_type:    "disaster"
amount_claimed: 15000000
province:       "Quảng Bình"
disaster_type:  "flood"
description:    "Nhà bị ngập lụt do bão số 5"
file:           [binary]
```

```json
// Response 201
{
  "claim_id": "...",
  "status": "pending",
  "message": "Claim submitted. AI processing started in background."
}
```

### GET `/claims`
```
// Query: ?status=approved&province=Quảng Bình&disaster_type=flood&page=1&page_size=10
```
```json
// Response 200
{
  "items": [
    {
      "id": "...",
      "claim_type": "disaster",
      "status": "approved",
      "amount_claimed": 15000000,
      "amount_approved": 12000000,
      "province": "Quảng Bình",
      "disaster_type": "flood",
      "ai_fraud_score": 8,
      "created_at": "...",
      "processed_at": "..."
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

### GET `/claims/{id}`
```json
// Response 200
{
  "id": "...",
  "status": "approved",
  "claim_type": "disaster",
  "disaster_type": "flood",
  "province": "Quảng Bình",
  "amount_claimed": 15000000,
  "amount_approved": 12000000,

  "ai_decision": "approved",
  "ai_reasoning": "Claim hợp lệ. Lũ lụt tháng 10/2024 tại Quảng Bình được ghi nhận lịch sử. Số tiền trong giới hạn bảo hiểm thiên tai 20,000,000 VND.",
  "ai_fraud_score": 8,
  "ai_fraud_flags": [],
  "ai_parsed_data": { "patient_name": null, "disaster_type": "flood", "damage_type": "residential" },

  "documents": [
    { "id": "...", "doc_type": "insurance_policy", "file_name": "hopd_bh.pdf" }
  ],

  "reviewer_id": null,
  "reviewer_note": null,
  "reviewed_at": null,

  "created_at": "...",
  "processed_at": "...",
  "updated_at": "..."
}
```

### PATCH `/claims/{id}/review`
Chỉ role `reviewer` hoặc `admin`. Yêu cầu `X-CSRF-Token`.
```json
// Request
{ "decision": "approved", "note": "Đã xác minh thiệt hại qua ảnh vệ tinh khu vực." }

// Response 200
{
  "id": "...",
  "status": "approved",
  "reviewer_id": "...",
  "reviewer_note": "Đã xác minh...",
  "reviewed_at": "2024-10-16T14:00:00Z"
}
// Error 403: không phải reviewer
// Error 400: claim không ở trạng thái manual_review
```

---

## Analytics

### GET `/analytics/summary`
```json
// Query: ?days=30
{
  "total_claims": 127,
  "pending_claims": 5,
  "approval_rate": 0.73,
  "avg_processing_seconds": 18.4,
  "total_amount_claimed": 185000000,
  "total_amount_approved": 134050000,
  "fraud_flagged_count": 8,
  "by_region": { "north": 45, "central": 62, "south": 20 },
  "by_disaster_type": { "flood": 38, "storm": 25, "landslide": 12, "other": 52 },
  "ocr_cache_hit_rate": 0.34
}
```

### GET `/analytics/daily`
```json
// Query: ?days=30
{
  "data": [
    {
      "date": "2024-10-15",
      "total": 12,
      "approved": 9,
      "rejected": 2,
      "manual_review": 1,
      "disaster_claims": 8,
      "avg_confidence": 0.87
    }
  ]
}
```

### GET `/analytics/breakdown`
```json
{
  "by_status": { "approved": 73, "rejected": 18, "manual_review": 12, "pending": 5 },
  "by_doc_type": { "cccd": 89, "insurance_policy": 95, "driver_license": 23 },
  "top_rejection_reasons": [
    { "reason": "Không thuộc phạm vi bảo hiểm", "count": 8 },
    { "reason": "Số tiền vượt giới hạn coverage", "count": 5 },
    { "reason": "Tài liệu không đủ / thiếu thông tin", "count": 3 }
  ],
  "low_confidence_rate": 0.12
}
```

---

## WebSocket

### `WS /ws/{claim_id}`

```json
// Khi processing
{ "event": "status_update", "status": "processing", "message": "Đang phân tích tài liệu..." }

// Khi xong — approved
{
  "event": "processing_complete",
  "status": "approved",
  "ai_decision": "approved",
  "ai_reasoning": "Claim hợp lệ...",
  "amount_approved": 12000000,
  "fraud_score": 8
}

// Khi cần manual review
{
  "event": "processing_complete",
  "status": "manual_review",
  "ai_decision": "manual_review",
  "fraud_score": 78,
  "fraud_flags": ["amount_anomaly", "provider_not_whitelisted"]
}

// Khi cần thêm thông tin (OCR confidence thấp)
{
  "event": "need_more_info",
  "status": "pending",
  "missing_fields": ["id_number", "expiry_date"],
  "low_confidence_fields": ["place_of_residence"],
  "message": "Vui lòng upload lại ảnh rõ hơn hoặc chỉnh sửa thông tin."
}

// Khi lỗi
{ "event": "processing_error", "status": "pending", "message": "Processing failed. Please retry." }
```

---

## TypeScript Types

```typescript
// types/document.ts
export type DocType =
  | 'cccd' | 'cmnd' | 'driver_license' | 'passport'
  | 'vehicle_registration' | 'insurance_policy' | 'other';

export type ProcessingStatus = 'pending' | 'processing' | 'done' | 'failed';

export interface ExtractedField {
  key: string;
  value: string | null;
  confidence: number;     // 0.0 - 1.0
  bbox?: number[];        // [x, y, w, h] cho visual highlighting
}

export interface EditHistoryEntry {
  field: string;
  old_value: string;
  new_value: string;
  edited_by: string;
  timestamp: string;
}

export interface DocumentDetail {
  id: string;
  doc_type: DocType;
  file_name: string;
  file_hash: string;
  file_size_kb: number;
  processing_status: ProcessingStatus;

  ocr_confidence: number | null;
  needs_manual_review: boolean;
  low_confidence_fields: string[];

  structured_data: Record<string, unknown>;
  extracted_fields: ExtractedField[];

  version: number;
  edit_history: EditHistoryEntry[];

  is_merged: boolean;
  merged_from: string[];
  merged_data: Record<string, unknown>;

  download_url: string;
  created_at: string;
  updated_at: string;
}

export interface MergeResult {
  merged_document_id: string;
  merged_data: Record<string, unknown>;
  conflicts: Record<string, { values: string[]; source_docs: string[] }>;
  stats: { total_fields: number; merged_clean: number; conflicts: number };
}

// types/geo.ts
export type Region = 'north' | 'central' | 'south';
export type DisasterType = 'storm' | 'flood' | 'landslide' | 'inundation' | 'drought';

export interface DisasterRisk {
  type: DisasterType;
  risk_score: number;
  frequency: 'high' | 'medium' | 'low';
  historical_events: number;
}

export interface InsuranceRecommendation {
  insurance_type: string;
  priority_score: number;
  reason: string;
  estimated_premium: string;
}

export interface ProvinceRisk {
  province_name: string;
  province_code: string;
  lat: number;
  lng: number;
  region: Region;
  overall_risk_score: number;
  is_high_risk: boolean;
  top_risk: DisasterType;
  risk_factors?: string[];
  disaster_risks?: DisasterRisk[];
  recommendations?: InsuranceRecommendation[];
}

export interface MapData {
  provinces: ProvinceRisk[];
  summary: { high_risk_count: number; medium_risk_count: number; low_risk_count: number };
}

// types/claim.ts
export type ClaimStatus = 'pending' | 'processing' | 'approved' | 'rejected' | 'manual_review';
export type ClaimType = 'medical' | 'dental' | 'hospitalization' | 'medication' | 'disaster';

export interface ClaimSummary {
  id: string;
  claim_type: ClaimType;
  status: ClaimStatus;
  amount_claimed: number;
  amount_approved: number | null;
  province: string | null;
  disaster_type: string | null;
  ai_fraud_score: number | null;
  created_at: string;
  processed_at: string | null;
}

export interface ClaimDetail extends ClaimSummary {
  ai_decision: string | null;
  ai_reasoning: string | null;
  ai_fraud_flags: string[];
  ai_parsed_data: Record<string, unknown> | null;
  reviewer_id: string | null;
  reviewer_note: string | null;
  reviewed_at: string | null;
  documents: { id: string; doc_type: DocType; file_name: string }[];
  updated_at: string;
}

// types/chatbot.ts
export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  session_id: string;
  response: string;
  suggested_actions?: { label: string; action: string; path: string }[];
}

export interface ChatSession {
  session_id: string;
  message_count: number;
  messages: ChatMessage[];
}

// types/analytics.ts
export interface AnalyticsSummary {
  total_claims: number;
  pending_claims: number;
  approval_rate: number;
  avg_processing_seconds: number;
  total_amount_claimed: number;
  total_amount_approved: number;
  fraud_flagged_count: number;
  by_region: Record<string, number>;
  by_disaster_type: Record<string, number>;
  ocr_cache_hit_rate: number;
}

export interface DailyStats {
  date: string;
  total: number;
  approved: number;
  rejected: number;
  manual_review: number;
  disaster_claims: number;
  avg_confidence: number;
}

// types/auth.ts
export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: 'user' | 'reviewer' | 'admin';
  province: string | null;
  region: 'north' | 'central' | 'south' | null;
  is_active: boolean;
}

// types/websocket.ts
export type WSEventType =
  | 'status_update'
  | 'processing_complete'
  | 'need_more_info'
  | 'processing_error';

export interface WSMessage {
  event: WSEventType;
  status: ClaimStatus;
  message?: string;
  ai_decision?: string;
  ai_reasoning?: string;
  amount_approved?: number;
  fraud_score?: number;
  fraud_flags?: string[];
  missing_fields?: string[];
  low_confidence_fields?: string[];
}
```

---

## Authorization Matrix

| Endpoint | User | Reviewer | Admin |
|---|:---:|:---:|:---:|
| `POST /auth/*` | ✓ | ✓ | ✓ |
| `POST /documents/upload` | ✓ | ✓ | ✓ |
| `POST /documents/merge` | ✓ | ✓ | ✓ |
| `GET /documents/{id}` | Own only | ✓ | ✓ |
| `POST /chatbot/message` | ✓ | ✓ | ✓ |
| `GET /geo-risk/*` | ✓ | ✓ | ✓ |
| `POST /claims/submit` | ✓ | ✓ | ✓ |
| `GET /claims` | Own only | All | All |
| `GET /claims/{id}` | Own only | All | All |
| `PATCH /claims/{id}/review` | ✗ | ✓ | ✓ |
| `GET /analytics/summary` | Own stats | All claims | Full system |
| **Admin only** | | | |
| `GET /admin/users` | ✗ | ✗ | ✓ |
| `PATCH /admin/users/{id}/role` | ✗ | ✗ | ✓ |
| `DELETE /admin/users/{id}` | ✗ | ✗ | ✓ |
| `GET /admin/policies` | ✗ | ✗ | ✓ |
| `POST /admin/policies` | ✗ | ✗ | ✓ |
| `DELETE /admin/policies/{id}` | ✗ | ✗ | ✓ |
| `GET /admin/audit-logs` | ✗ | ✗ | ✓ |
| `GET /admin/system/health` | ✗ | ✗ | ✓ |
| `GET /admin/analytics/full` | ✗ | ✗ | ✓ |

---

## Admin Endpoints

> Tất cả `/admin/*` endpoints yêu cầu role `admin`. Trả 403 nếu không phải admin.

### GET `/admin/users`
```json
// Query: ?role=reviewer&is_active=true&page=1&page_size=20
// Response 200
{
  "items": [
    {
      "id": "...",
      "email": "reviewer@covergo.com",
      "full_name": "Trần Thị B",
      "role": "reviewer",
      "province": "Hà Nội",
      "region": "north",
      "is_active": true,
      "claims_reviewed": 47,
      "created_at": "...",
      "last_login": "..."
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20
}
```

### PATCH `/admin/users/{id}/role`
```json
// Request
{ "role": "reviewer" }

// Response 200
{ "id": "...", "email": "...", "role": "reviewer", "updated_at": "..." }

// Error 400: không thể tự đổi role của chính mình
{ "detail": "Cannot change your own role" }
```

### PATCH `/admin/users/{id}/status`
```json
// Request — deactivate/activate user
{ "is_active": false, "reason": "Vi phạm điều khoản sử dụng" }

// Response 200
{ "id": "...", "is_active": false, "updated_at": "..." }
```

### DELETE `/admin/users/{id}`
```json
// Response 200
{ "message": "User deactivated. Data retained for audit." }
// Soft delete — không xóa vật lý, chỉ set is_active=false
```

### GET `/admin/policies`
```json
// Response 200 — quản lý policy documents cho RAG
{
  "items": [
    {
      "id": "...",
      "title": "Điều khoản bảo hiểm y tế 2024",
      "category": "medical",
      "version": "2024.1",
      "is_active": true,
      "chunk_count": 48,
      "last_ingested": "2024-05-01T00:00:00Z",
      "created_at": "..."
    }
  ],
  "total": 6
}
```

### POST `/admin/policies`
`multipart/form-data`:
```
file:     [binary]    .txt hoặc .pdf
title:    "Điều khoản bảo hiểm bão lũ 2024"
category: "disaster"
version:  "2024.1"
```
```json
// Response 201
{
  "policy_id": "...",
  "title": "...",
  "message": "Policy uploaded. Ingesting vào Qdrant vector store...",
  "chunk_count": 52
}
```

### DELETE `/admin/policies/{id}`
```json
// Response 200
{
  "message": "Policy deactivated and removed from vector store.",
  "chunks_deleted": 52
}
```

### GET `/admin/audit-logs`
```json
// Query: ?action=role_change&user_id=...&from=2024-05-01&to=2024-05-31&page=1
// Response 200
{
  "items": [
    {
      "id": "...",
      "timestamp": "2024-05-15T10:30:00Z",
      "actor_id": "admin-user-id",
      "actor_email": "admin@covergo.com",
      "action": "role_change",
      "target_type": "user",
      "target_id": "...",
      "details": {
        "old_role": "user",
        "new_role": "reviewer",
        "reason": "Promoted to claims reviewer team"
      }
    }
  ],
  "total": 234
}
// action types: role_change | user_deactivate | policy_upload
//               policy_delete | claim_override | login_failed
```

### GET `/admin/system/health`
```json
// Response 200
{
  "status": "healthy",
  "timestamp": "2024-05-15T10:30:00Z",
  "services": {
    "mongodb": { "status": "ok", "latency_ms": 2 },
    "redis": { "status": "ok", "latency_ms": 1 },
    "qdrant": { "status": "ok", "latency_ms": 5 },
    "minio": { "status": "ok", "latency_ms": 8 },
    "gemini_api": { "status": "ok", "quota_remaining": 1243 }
  },
  "celery": {
    "workers_online": 1,
    "queue_depth": 3,
    "tasks_processed_today": 127
  }
}
```

### GET `/admin/analytics/full`
```json
// Query: ?days=30
// Response 200 — full system analytics (không filter theo user)
{
  "overview": {
    "total_users": 150,
    "active_users_30d": 89,
    "new_users_7d": 12,
    "total_documents_ocr": 1247,
    "ocr_cache_hit_rate": 0.34,
    "avg_ocr_confidence": 0.87,
    "total_claims": 534,
    "approval_rate": 0.73,
    "avg_processing_seconds": 18.4,
    "fraud_flagged_rate": 0.06
  },
  "by_region": { "north": 189, "central": 245, "south": 100 },
  "by_doc_type": { "cccd": 512, "insurance_policy": 389, "driver_license": 156 },
  "by_disaster_type": { "flood": 145, "storm": 98, "landslide": 42 },
  "top_high_risk_provinces": [
    { "province": "Quảng Bình", "claims_count": 47, "risk_score": 92 },
    { "province": "Hà Tĩnh", "claims_count": 38, "risk_score": 89 }
  ],
  "reviewer_performance": [
    {
      "reviewer_id": "...",
      "reviewer_name": "Trần Thị B",
      "claims_reviewed": 47,
      "avg_review_time_minutes": 12,
      "override_rate": 0.08
    }
  ]
}
```

---

## Reviewer Endpoints

### GET `/reviewer/queue`
```json
// Claims cần review — chỉ status=manual_review
// Query: ?province=Quảng Bình&sort=oldest_first&page=1
{
  "items": [
    {
      "id": "...",
      "status": "manual_review",
      "claim_type": "disaster",
      "province": "Quảng Bình",
      "amount_claimed": 30000000,
      "ai_fraud_score": 78,
      "ai_fraud_flags": ["amount_anomaly", "provider_not_whitelisted"],
      "submitted_by": { "id": "...", "full_name": "Nguyễn Văn A" },
      "created_at": "...",
      "waiting_since": "2 hours ago"
    }
  ],
  "total": 12
}
```

### GET `/reviewer/stats`
```json
// Stats cá nhân của reviewer đang login
{
  "claims_reviewed_today": 5,
  "claims_reviewed_total": 47,
  "pending_in_queue": 12,
  "avg_review_time_minutes": 12,
  "override_rate": 0.08
}
```

---

## TypeScript Types bổ sung

```typescript
// types/admin.ts
export type UserRole = 'user' | 'reviewer' | 'admin';

export interface AdminUser {
  id: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  province: string | null;
  region: string | null;
  is_active: boolean;
  claims_reviewed: number;
  created_at: string;
  last_login: string | null;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  actor_id: string;
  actor_email: string;
  action: 'role_change' | 'user_deactivate' | 'policy_upload'
        | 'policy_delete' | 'claim_override' | 'login_failed';
  target_type: 'user' | 'policy' | 'claim';
  target_id: string;
  details: Record<string, unknown>;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down';
  timestamp: string;
  services: Record<string, { status: 'ok' | 'error'; latency_ms: number }>;
  celery: { workers_online: number; queue_depth: number; tasks_processed_today: number };
}

export interface AdminAnalytics {
  overview: {
    total_users: number;
    active_users_30d: number;
    new_users_7d: number;
    total_documents_ocr: number;
    ocr_cache_hit_rate: number;
    avg_ocr_confidence: number;
    total_claims: number;
    approval_rate: number;
    avg_processing_seconds: number;
    fraud_flagged_rate: number;
  };
  by_region: Record<string, number>;
  by_doc_type: Record<string, number>;
  by_disaster_type: Record<string, number>;
  top_high_risk_provinces: { province: string; claims_count: number; risk_score: number }[];
  reviewer_performance: {
    reviewer_id: string;
    reviewer_name: string;
    claims_reviewed: number;
    avg_review_time_minutes: number;
    override_rate: number;
  }[];
}

export interface PolicyDocument {
  id: string;
  title: string;
  category: string;
  version: string;
  is_active: boolean;
  chunk_count: number;
  last_ingested: string;
  created_at: string;
}

export interface ReviewerQueueItem {
  id: string;
  status: 'manual_review';
  claim_type: string;
  province: string | null;
  amount_claimed: number;
  ai_fraud_score: number;
  ai_fraud_flags: string[];
  submitted_by: { id: string; full_name: string };
  created_at: string;
  waiting_since: string;
}
```
