# Soulee (SLE) — API Documentation

> Tổng hợp từ toàn bộ tiến độ backend đã implement thực tế: **Phase 0 → Phase 8 + B.6** (System Config Wiring) và **Phase 10.1** (OpenAPI → TypeScript types).
> Base URL: `/api/v1` · Auth: JWT Bearer · Format: JSON
> Tổng: **40 endpoints**

⚠️ **Lưu ý quan trọng về format response:** Tài liệu thiết kế gốc quy định toàn bộ response theo chuẩn envelope `{ success, data, pagination }`. Trong thực tế implement:
- Chỉ **5 endpoint Auth** (`register`, `login`, `refresh`, `logout`, `logout-all`) được bọc `SuccessEnvelope[T]` (`{"success": true, "data": {...}}`) — sửa ở Phase 10.1 để có type generation đúng.
- **Các endpoint còn lại trả trực tiếp schema** (không bọc `success/data`), ví dụ `GET /users/me` trả thẳng `UserProfile`, không phải `{success, data: UserProfile}`.
- Danh sách có pagination trả `{ items, total, page, page_size }` hoặc `{ items, total, page, limit }` tùy endpoint (không đồng nhất 100% — ghi chú cụ thể ở từng mục).

---

## Quy ước chung

### Authentication
- Access token: JWT, gửi qua header `Authorization: Bearer <access_token>`, TTL **15 phút**
- Refresh token: opaque random string, gửi qua **request body** (không phải cookie), lưu hash SHA-256 trong DB, TTL 7 ngày
- Refresh token rotation: mỗi lần refresh, token cũ bị revoke và cấp cặp token mới hoàn toàn

### Error format (chuẩn HTTPException của FastAPI)
```json
{
  "detail": "Error message"
}
```
hoặc dạng có cấu trúc hơn ở một số nơi (ví dụ auth):
```json
{
  "detail": {
    "success": false,
    "error": { "code": "REGISTRATION_DISABLED", "message": "..." }
  }
}
```

### Phân trang (không đồng nhất giữa các nhóm endpoint)
| Nhóm | Field phân trang |
|---|---|
| Cards | `items, total, page, page_size` |
| Sessions history | `items, total, page, limit` |
| Admin lists | `items/list, total, page, ...` (theo từng endpoint, xem chi tiết) |

---

## 1. Authentication — `/auth`

Bọc `SuccessEnvelope[T]`: `{"success": true, "data": {...}}`

### `POST /api/v1/auth/register` → 201
Đăng ký user mới.
- Kiểm tra `config.allow_registration` trước (nếu `false` → 403 `REGISTRATION_DISABLED`)
- Kiểm tra email trùng → 409 `EMAIL_TAKEN`
- Hash password bằng bcrypt

**Response `data`:**
```json
{
  "user": { "id": "uuid", "email": "...", "display_name": "...", "avatar_url": null, "role": "user", "streak": 0, "..." : "..." },
  "tokens": { "access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 900 }
}
```

### `POST /api/v1/auth/login` → 200
- `authenticate_user` trả `None` thống nhất cho "sai email" / "sai password" / "user bị ban" → tránh **user enumeration attack**
- Response `data` giống `register` (`user` + `tokens`)

### `POST /api/v1/auth/refresh` → 200
Request body: `{ "refresh_token": "..." }`
- SHA-256 hash token nhận được → tìm trong DB, validate còn hạn + chưa revoke + user active
- Revoke token cũ, issue cặp token mới hoàn toàn (rotation)
- Response `data`: `{ "access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 900 }`

### `POST /api/v1/auth/logout` → 200
Request body: `{ "refresh_token": "..." }` — revoke đúng token này.
Response `data`: `{ "message": "..." }`

### `POST /api/v1/auth/logout-all` → 200
Revoke **toàn bộ** refresh token của user hiện tại (mọi thiết bị).
Response `data`: `{ "message": "..." }`

---

## 2. User Profile — `/users`

Trả **trực tiếp schema**, không bọc envelope.

### `GET /api/v1/users/me` → 200
Trả `UserProfile` từ `get_current_user` dependency (không query DB thêm).

### `PATCH /api/v1/users/me` → 200
Partial update `display_name` và/hoặc `avatar_url`. Validate ít nhất 1 field phải có trong body (request rỗng → lỗi).
Response: `UserProfile` đã cập nhật.

### `PATCH /api/v1/users/me/password` → 204 No Content
Request: `{ "old_password": "...", "new_password": "..." }`
- Verify `old_password` bằng bcrypt trước khi hash `new_password`
- Không trả body (đúng chuẩn REST cho action thành công không cần trả data)

### `POST /api/v1/users/me/avatar` → 200
Multipart form-data, field `file`.
- Content-type cho phép: `image/jpeg`, `image/png`, `image/webp`, `image/gif`
- Size tối đa: `config.max_image_size_mb` (default 5MB)
- Object path MinIO: `avatars/{user_id}/avatar.{ext}` (overwrite khi upload lại)

Response:
```json
{ "avatar_url": "http://localhost:9000/avatars/{user_id}/avatar.jpg", "message": "Avatar updated successfully" }
```

---

## 3. Folders — `/folders`

### `GET /api/v1/folders` → 200
Danh sách folder của user hiện tại, sắp xếp A-Z.

### `POST /api/v1/folders` → 201
Request: `{ "name": "...", "description": "..." }` — `name` unique theo `(owner_id, name)`, trùng → 409.

### `GET /api/v1/folders/{id}` → 200
Chi tiết 1 folder (chỉ owner).

### `PATCH /api/v1/folders/{id}` → 200
Partial update, dùng `model_dump(exclude_unset=True)` để phân biệt "không gửi field" vs "gửi null".

### `DELETE /api/v1/folders/{id}` → 204
Xóa folder — **không cascade** sang sets (DB `ON DELETE SET NULL folder_id`, sets vẫn tồn tại).

---

## 4. Study Sets — `/sets`

### `GET /api/v1/sets` → 200
Query params:
| Param | Ví dụ | Mô tả |
|---|---|---|
| `search` | `?search=vocabulary` | Full-text search (title + description), dùng `plainto_tsquery("simple", ...)` |
| `folder_id` | `?folder_id=uuid` | Lọc theo folder |

Có thể kết hợp cả 2 params.

### `POST /api/v1/sets` → 201
Request: `{ "title": "...", "description": "...", "tags": [...], "is_public": false, "folder_id": "uuid|null" }`
- Bị chặn 400 nếu đã đạt `config.max_sets_per_user` (default 50)

### `GET /api/v1/sets/{id}` → 200
Xem được nếu: là owner, **hoặc** set `is_public = true`. Không tồn tại/không đủ quyền → trả `None` thống nhất (tránh leak thông tin) → 404.

### `PATCH /api/v1/sets/{id}` → 200
Chỉ owner. `folder_id` có 3 case: không gửi = giữ nguyên; `null` = bỏ khỏi folder; UUID = chuyển folder (validate ownership).

### `DELETE /api/v1/sets/{id}` → 204
Chỉ owner, cascade xóa cards.

### `POST /api/v1/sets/{id}/clone` → 201
Nhân bản set public (hoặc set mình sở hữu) thành set riêng mới:
- `is_public=False`, `folder_id=None`, `cloned_from={original.id}` cho set mới
- Copy toàn bộ cards (giữ front/back/image_url/order)
- Ghi 1 record vào `set_clones` (analytics), unique theo `(original_set_id, cloned_by)`
- Toàn bộ nằm trong 1 transaction (dùng `flush()` trước `commit()`)

Response (ví dụ):
```json
{
  "id": "uuid-set-mới", "owner_id": "uuid-của-bạn", "title": "English Phrasal Verbs",
  "is_public": false, "folder_id": null, "card_count": 4, "cloned_from": "uuid-set-gốc"
}
```

---

## 5. Cards — `/sets/{set_id}/cards`

### `GET /api/v1/sets/{set_id}/cards` → 200
Pagination `?page=1&page_size=50` (max 200). Xem được nếu owner hoặc set public.
Response: `CardListResponse` = `{ items: [...], total, page, page_size }` (schema riêng, sửa ở Phase 10.1 — trước đó trả `dict` rỗng type).

### `POST /api/v1/sets/{set_id}/cards` → 201
Chỉ owner. `order` mới = `max(order) + 1.0` (luôn append cuối).
Bị chặn 400 nếu đạt `config.max_cards_per_set` (default 500) — dùng trực tiếp `study_set.card_count` (đã có sẵn, đồng bộ bởi DB trigger `trg_card_count`, không cần `COUNT(*)` lại.

### `GET /api/v1/sets/{set_id}/cards/{card_id}` → 200
### `PATCH /api/v1/sets/{set_id}/cards/{card_id}` → 200
Partial update, chỉ owner.
### `DELETE /api/v1/sets/{set_id}/cards/{card_id}` → 204
Chỉ owner. DB trigger tự `-1 card_count`.

### `PATCH /api/v1/sets/{set_id}/cards/{card_id}/order` → 200
Reorder bằng FLOAT `order` — chỉ update **1 row**:

| Trường hợp | Công thức |
|---|---|
| Lên đầu | `next_order - 1.0` |
| Xuống cuối | `prev_order + 1.0` |
| Chèn giữa 2 card | `(prev_order + next_order) / 2.0` |
| Không có card nào | `1.0` |

Rebalance tự động khi `abs(new_order - neighbor_order) < 1e-9`: reset toàn bộ về `1.0, 2.0, 3.0, ...` theo thứ tự hiện tại.
Validator: `prev_order < next_order` nếu cả 2 được gửi, ngược lại → 422.

### `POST /api/v1/sets/{set_id}/cards/{card_id}/image` → 200
Multipart, field `file`. Chỉ owner.
- Content-type: `image/jpeg`, `image/png`, `image/webp`
- Size tối đa: `config.max_image_size_mb`
- Object path: `card-images/{card_id}/image.{ext}` (overwrite)

Response: cập nhật `cards.image_url`, trả public URL.

---

## 6. Study Sessions & Progress (SM-2) — `/sessions`

### SM-2 Engine (thuần logic, không truy cập DB)

Constants (từ Phase 6; **từ B.6 đọc động từ `SystemConfig`**, không hardcode):
```
initial_ease_factor  = 2.5   (config.initial_ease_factor)
min_ease_factor       = 1.3   (config.min_ease_factor)
known_threshold_days  = 7     (config.known_threshold_days)
```

Công thức:
| Kết quả | Công thức |
|---|---|
| Đúng (`quality >= 3`) | `new_ef = max(min_ease_factor, ef + 0.1 - (5 - q) * 0.08)`; `new_interval = round(max(1, interval) * new_ef)` |
| Sai (`quality < 3`) | `new_ef = max(min_ease_factor, ef - 0.2)`; `interval = 1`; `repetitions = 0` |

`status` derive runtime (không lưu DB): `interval >= known_threshold_days` → `known`, ngược lại → `learning`; chưa có progress → `not_started`.

`map_quality()`:
| Mode | Logic |
|---|---|
| `learn` | Dùng `explicit_quality` (1–5) do user chọn, bắt buộc |
| `flashcard / test / match` | Auto-map: đúng → quality 4, sai → quality 1 |

### `POST /api/v1/sessions` → 201
Request: `{ "set_id": "uuid", "mode": "flashcard|learn|test|match" }`
- Kiểm tra quyền: owner hoặc set public
- Tạo `study_sessions` row (`ended_at = NULL`)
- Lấy cards "due" (`next_review <= now()` hoặc chưa có progress); fallback trả toàn bộ cards nếu không card nào due

Response:
```json
{
  "id": "uuid", "set_id": "uuid", "mode": "flashcard", "started_at": "...",
  "cards": [ { "id": "uuid", "front": "...", "back": "...", "status": "not_started", "next_review": null } ]
}
```

### `POST /api/v1/sessions/{session_id}/answers` → 200
Request body:
```json
{ "card_id": "uuid", "is_correct": true, "explicit_quality": 4, "user_answer": "...", "time_spent": 1200 }
```
(`explicit_quality` bắt buộc nếu mode = `learn`)

Logic: kiểm tra session còn mở (`ended_at IS NULL`) → map quality → lấy `StudyProgress` hiện tại → tính SM-2 mới → **upsert** `study_progress` → insert `session_answers` (snapshot front/back tại thời điểm trả lời) → cập nhật counters session.

Response:
```json
{
  "card_id": "uuid", "is_correct": true, "quality": 4,
  "sm2": { "ease_factor": 2.52, "interval": 3, "repetitions": 1, "next_review": "...", "status": "learning" }
}
```

### `POST /api/v1/sessions/{session_id}/end` → 200
Kết thúc session: set `ended_at = now()`, tính `accuracy`, gọi `update_streak()`, tính `duration_seconds`.

Response:
```json
{
  "id": "uuid", "mode": "flashcard", "started_at": "...", "ended_at": "...",
  "duration_seconds": 60, "cards_studied": 1, "correct": 1, "incorrect": 0, "accuracy": 100.0
}
```

**Streak logic** (tính theo ngày UTC, không phải 24h rolling):
| Điều kiện | Hành động |
|---|---|
| `last_studied IS NULL` | `streak = 1` |
| `last == today` | Giữ nguyên |
| `last == today - 1` | `streak += 1` |
| `last < today - 1` | `streak = 1` (reset) |

### `GET /api/v1/sessions` → 200
Query: `set_id`, `mode`, `page` (default 1), `limit` (default 10, max 100).
Chỉ trả sessions `ended_at IS NOT NULL`, JOIN lấy `set_title`, sort `ended_at DESC`.

Response: `{ items: [...], total, page, limit }`.

---

## 7. Statistics — `/stats`

### `GET /api/v1/stats/overview` → 200
```json
{
  "streak": 1, "last_studied": "...", "total_cards_known": 1, "total_cards_learning": 0,
  "total_sessions": 1, "total_study_time_seconds": 60, "sets_studied": 1
}
```
Note kỹ thuật: 1 card có thể có nhiều `study_progress` (1 row/mode) — classify known/learning dựa trên `max(interval)` per card qua subquery, tránh đếm trùng.

### `GET /api/v1/stats/sessions` → 200
Query: `range` (`7d`/`30d`/`90d`, default `7d`, alias vì `range` là builtin Python), `group_by` (`day`/`week`, default `day`).
Trả đủ mọi ngày trong range, **zero-fill** ngày không có dữ liệu.

```json
{
  "range": "7d", "group_by": "day",
  "data": [ { "date": "2026-06-11", "sessions": 0, "cards_studied": 0, "correct": 0, "accuracy": 0, "study_time_seconds": 0 }, "..." ]
}
```

### `GET /api/v1/sets/{set_id}/stats` → 200
> Nằm trên `sets_router` (không phải `stats_router`) để URL đúng REST convention.

Phân quyền: 404 nếu set không tồn tại; 403 nếu private + không phải owner.

```json
{
  "set_id": "uuid", "set_title": "...", "card_count": 6,
  "progress_summary": { "known": 0, "learning": 0, "not_started": 6, "known_rate": 0 },
  "by_mode": [ { "mode": "flashcard", "sessions": 1, "avg_accuracy": 100, "last_studied": "..." } ],
  "total_sessions": 0, "total_study_time_seconds": 0
}
```

---

## 🛡️ Admin APIs — tất cả yêu cầu `role = "admin"` (403 nếu không phải admin)

### A1. Dashboard

#### `GET /api/v1/admin/dashboard?range=7d|30d|90d` → 200
Trả: user metrics (`total/active/inactive/new_today/new_7d`), set metrics (`total/public/private`), session metrics (`today/7d/30d`), `DAU/MAU`, `user_growth` chart, `session_chart` — đều zero-fill đủ ngày trong range.

### A2. User Management

| Endpoint | Mô tả |
|---|---|
| `GET /api/v1/admin/users` | List + search + filter (`role`, `is_active`) + sort + pagination |
| `GET /api/v1/admin/users/{user_id}` | Chi tiết: profile + stats + devices (`refresh_tokens`) + 5 session gần nhất |
| `PATCH /api/v1/admin/users/{user_id}` | Ban/unban, cấp/thu hồi admin, force reset password |
| `DELETE /api/v1/admin/users/{user_id}` | Xóa cascade toàn bộ dữ liệu liên quan |

**Cơ chế self-protection (đã test kỹ):**
| Cơ chế | Hành vi |
|---|---|
| Ban user (`is_active=false`) | Tự động revoke toàn bộ `refresh_tokens` |
| Admin tự ban chính mình | 400 |
| Admin tự thu hồi quyền admin của mình | 400 |
| Admin tự xóa chính mình | 400 |
| `PATCH` body rỗng `{}` | 400 — "No update fields provided" |
| Force reset password | Password ngẫu nhiên (`secrets.token_urlsafe(9)`), hash bcrypt, revoke hết refresh_tokens |

> Lưu ý bảo mật cố ý: login với account bị ban trả cùng message `"Email or password is incorrect"` như sai password — không lộ trạng thái tài khoản.

### A3. Study Set Management

| Endpoint | Mô tả |
|---|---|
| `GET /api/v1/admin/sets` | List **tất cả** sets (kể cả private) + filter (`owner_id`, `is_public`) + sort (hỗ trợ `session_count`, `clone_count`) + pagination |
| `PATCH /api/v1/admin/sets/{set_id}` | Toggle `is_public` (content moderation) |
| `DELETE /api/v1/admin/sets/{set_id}` | Xóa cascade |

### A4. Statistics

| Endpoint | Mô tả |
|---|---|
| `GET /api/v1/admin/stats/users` | `growth` chart, `streak_distribution` (4 bucket: 0 / 1-7 / 8-30 / 30+), `churn_rate` (>30 ngày không học) |
| `GET /api/v1/admin/stats/learning` | `sessions_chart`, `mode_distribution` (sessions + avg_accuracy theo mode), `avg_known_rate`, `avg_accuracy` |
| `GET /api/v1/admin/stats/content` | Top 10 sets by sessions, top 10 by clones, `popular_tags` (dùng `func.unnest()` trên cột ARRAY `tags`) |

### A5. System Config

| Endpoint | Mô tả |
|---|---|
| `GET /api/v1/admin/config` | Đọc config hiện tại |
| `PATCH /api/v1/admin/config` | Update 1 hoặc nhiều field |

**`SystemConfig` fields** (bảng single-row, `id` luôn = 1):
| Field | Type | Default | Áp dụng tại (đã wire — B.6) |
|---|---|---|---|
| `initial_ease_factor` | float | 2.5 | SM-2: ease factor khởi điểm cho card chưa học |
| `min_ease_factor` | float | 1.3 | SM-2: ease factor không giảm dưới ngưỡng này |
| `known_threshold_days` | int | 7 | Ngưỡng `interval` để tính "known" (đồng bộ ở `sessions.py`, `stats_service.py`, `admin_service.py`) |
| `max_sets_per_user` | int | 50 | Chặn tạo set mới khi vượt (400) |
| `max_cards_per_set` | int | 500 | Chặn tạo card mới khi vượt (400) |
| `max_image_size_mb` | int | 5 | Chặn upload ảnh vượt dung lượng (avatar + card image) |
| `allow_registration` | bool | true | Khóa/mở đăng ký mới toàn hệ thống |

Validation: `min_ease_factor` không được lớn hơn `initial_ease_factor` → 400 nếu vi phạm.

---

## Tổng hợp toàn bộ endpoint (40)

```
# Auth (5)
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
POST   /api/v1/auth/logout-all

# Users (4)
GET    /api/v1/users/me
PATCH  /api/v1/users/me
PATCH  /api/v1/users/me/password
POST   /api/v1/users/me/avatar

# Folders (5)
GET    /api/v1/folders
POST   /api/v1/folders
GET    /api/v1/folders/{id}
PATCH  /api/v1/folders/{id}
DELETE /api/v1/folders/{id}

# Study Sets (6)
GET    /api/v1/sets
POST   /api/v1/sets
GET    /api/v1/sets/{id}
PATCH  /api/v1/sets/{id}
DELETE /api/v1/sets/{id}
POST   /api/v1/sets/{id}/clone

# Cards (7)
GET    /api/v1/sets/{set_id}/cards
POST   /api/v1/sets/{set_id}/cards
GET    /api/v1/sets/{set_id}/cards/{card_id}
PATCH  /api/v1/sets/{set_id}/cards/{card_id}
DELETE /api/v1/sets/{set_id}/cards/{card_id}
PATCH  /api/v1/sets/{set_id}/cards/{card_id}/order
POST   /api/v1/sets/{set_id}/cards/{card_id}/image

# Sessions (4)
POST   /api/v1/sessions
POST   /api/v1/sessions/{session_id}/answers
POST   /api/v1/sessions/{session_id}/end
GET    /api/v1/sessions

# Stats (3)
GET    /api/v1/stats/overview
GET    /api/v1/stats/sessions
GET    /api/v1/sets/{set_id}/stats

# Admin (13)
GET    /api/v1/admin/dashboard
GET    /api/v1/admin/users
GET    /api/v1/admin/users/{user_id}
PATCH  /api/v1/admin/users/{user_id}
DELETE /api/v1/admin/users/{user_id}
GET    /api/v1/admin/sets
PATCH  /api/v1/admin/sets/{set_id}
DELETE /api/v1/admin/sets/{set_id}
GET    /api/v1/admin/stats/users
GET    /api/v1/admin/stats/learning
GET    /api/v1/admin/stats/content
GET    /api/v1/admin/config
PATCH  /api/v1/admin/config
```

---

## Type-safety FE ↔ BE (Phase 10.1)

- Types sinh tự động từ `/openapi.json` qua `openapi-typescript` → `packages/types/api.d.ts`
- Import trong Next.js: `import type { components } from "@repo/types"` (scope thực tế là `@repo/`, không phải `@sle/` như tài liệu thiết kế gốc)
- 5 endpoint auth dùng schema `SuccessEnvelope_RegisterResponse_`, `SuccessEnvelope_LoginResponse_`, `SuccessEnvelope_RefreshResponse_`, `SuccessEnvelope_MessageData_` (đặt tên tự động bởi `openapi-typescript`, thay `[]` bằng `_`)
- `GET /sets/{set_id}/cards` dùng schema `CardListResponse`
- Chạy `npm run generate:types` (trong `packages/types`) mỗi khi backend đổi schema
