# SLE Backend — Tài liệu Thiết kế Hoàn chỉnh
**Self-Learning English Platform · Flashcard Core**

> Tài liệu này phản ánh **backend đã triển khai thực tế** (Phase 0 → Phase 8 + B.6 + Phase 10.1), tổng hợp từ tài liệu thiết kế gốc, các báo cáo tiến độ theo phase, và API documentation. Những chỗ thực tế khác với thiết kế ban đầu đều được ghi chú rõ. Trạng thái: **40 endpoints, sẵn sàng cho Phase 9 (Frontend)**.

---

## Mục lục

1. [Tổng quan kiến trúc & Tech Stack](#1-tổng-quan-kiến-trúc--tech-stack)
2. [Cấu trúc Monorepo & Docker](#2-cấu-trúc-monorepo--docker)
3. [Database Schema](#3-database-schema)
4. [Quy ước API chung](#4-quy-ước-api-chung)
5. [API Reference — User](#5-api-reference--user)
6. [API Reference — Admin](#6-api-reference--admin)
7. [SM-2 Spaced Repetition Engine](#7-sm-2-spaced-repetition-engine)
8. [System Config (Runtime-configurable)](#8-system-config-runtime-configurable)
9. [Type Sharing FE ↔ BE](#9-type-sharing-fe--be)
10. [Quyết định kiến trúc & Gotcha quan trọng](#10-quyết-định-kiến-trúc--gotcha-quan-trọng)
11. [Việc còn lại — Phase 9 & 10.2](#11-việc-còn-lại--phase-9--102)

---

## 1. Tổng quan kiến trúc & Tech Stack

```
┌──────────────────────────────────────────────────────┐
│                     FRONTEND                          │
│  Next.js 16 (App Router) · TypeScript                 │
│  shadcn/ui · TanStack Query · Zustand                  │
│  React Hook Form + Zod · Axios                          │
└──────────────────────┬───────────────────────────────┘
                        │  REST API / JSON
┌──────────────────────▼───────────────────────────────┐
│                     BACKEND                            │
│  FastAPI 0.115 (Python 3.12) · Pydantic v2              │
│  SQLAlchemy 2.x (async) · Alembic migrations             │
│  python-jose (JWT) · passlib (bcrypt)                     │
│  Celery + Redis (background jobs, thay cho pg_cron)         │
└────┬──────────┬──────────┬────────────────────────────┘
     │          │          │
┌────▼───┐ ┌────▼───┐ ┌───▼────┐
│Postgres│ │ Redis  │ │  MinIO │
│16      │ │7-alpine│ │        │
│pgvector│ │Cache/  │ │Files   │
│ready   │ │Celery  │ │(avatar,│
│        │ │broker  │ │ card   │
│        │ │        │ │ image) │
└────────┘ └────────┘ └────────┘
```

| Layer | Công nghệ | Version thực tế |
|---|---|---|
| Frontend | Next.js (App Router) | 16.x |
| Frontend UI | shadcn/ui + Tailwind CSS | latest |
| Frontend State | Zustand | latest |
| Frontend Data | TanStack Query | latest |
| Frontend Forms | React Hook Form + Zod | latest |
| Backend | FastAPI | 0.115.0 |
| Backend Runtime | Python | 3.12.10 |
| Backend ORM | SQLAlchemy (async) | 2.0.36 |
| Backend Validation | Pydantic v2 | 2.9.2 |
| Auth | python-jose (JWT) + passlib (bcrypt) | 3.3.0 / 1.7.4 |
| Database | PostgreSQL + pgvector | pg16 |
| Cache / Queue | Redis + Celery | 7-alpine / 5.4.0 |
| File Storage | MinIO | latest |
| Monorepo | Turborepo | 2.9.14 |
| Container | Docker Compose | — |
| Node | Node.js | 24.13.0 |

**Khác biệt so với thiết kế gốc:** thiết kế gốc dự kiến dùng `pg_cron` để dọn refresh token hết hạn, nhưng extension này **không có sẵn** trong image `pgvector/pgvector:pg16` → thay bằng **Celery Beat task** (implement ở Phase 6, cùng lúc với hạ tầng Celery cho SM-2/streak).

---

## 2. Cấu trúc Monorepo & Docker

### Cấu trúc thư mục thực tế

```
sle/
├── apps/
│   ├── api/                          # FastAPI backend
│   │   ├── app/
│   │   │   ├── core/                 # config.py, database.py, security.py
│   │   │   ├── routers/              # auth, users, folders, sets, cards, sessions, stats, admin
│   │   │   ├── schemas/              # + common.py (SuccessEnvelope[T])
│   │   │   ├── services/             # + config_service.py
│   │   │   ├── models/               # user, content, learning, config
│   │   │   └── dependencies.py       # get_current_user, require_admin
│   │   ├── alembic/versions/         # 001_core → 002_content → 003_learning → 004_system_config
│   │   └── main.py
│   └── web/                          # Next.js 16 (Phase 9 — chưa làm)
│       ├── app/(auth)/ (dashboard)/
│       ├── components/ui, layout/
│       ├── lib/api-client.ts, utils.ts
│       ├── store/, hooks/
├── packages/
│   ├── eslint-config/
│   ├── typescript-config/
│   ├── ui/
│   └── types/                        # @repo/types — auto-gen từ OpenAPI
├── docker-compose.yml
└── turbo.json
```

> ⚠️ **Khác biệt quan trọng so với thiết kế gốc:** thiết kế gốc ghi scope package là `@sle/types`, nhưng monorepo tạo bằng `create-turbo` thực tế dùng scope **`@repo/`** (khớp với `@repo/eslint-config`, `@repo/ui` có sẵn từ Phase 0). Package chia sẻ type đặt tên đúng là **`@repo/types`**, không phải `@sle/types`.

### Docker Compose — 6 services

| Service | Image | Port | Ghi chú |
|---|---|---|---|
| postgres | `pgvector/pgvector:pg16` | 5432 | Có sẵn pgvector cho V2 |
| redis | `redis:7-alpine` | 6379 | Cache + Celery broker |
| minio | `minio/minio:latest` | 9000 / 9001 | Console: `minioadmin/minioadmin123` |
| api | `apps/api/Dockerfile` | 8000 | `profiles: ["app"]` |
| celery | `apps/api/Dockerfile` | — | `profiles: ["app"]` |
| web | `apps/web/Dockerfile` | 3000 | `profiles: ["app"]` |

Chạy hạ tầng dev (không cần build app):
```bash
docker compose up -d postgres redis minio
```

Chạy backend local (không qua Docker):
```bash
cd apps/api && .venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

---

## 3. Database Schema

PostgreSQL 16, SQLAlchemy 2.x (async), Alembic. Extensions: `pgcrypto`, `pg_trgm`, `unaccent`, `vector` (`pg_cron` **không dùng** — xem mục 1).

10 bảng qua 4 migration: `001_core`, `002_content`, `003_learning`, `004_system_config`.

### 3.1 `users` (migration 001)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | UUID PK | `gen_random_uuid()` |
| `email` | VARCHAR(255) UNIQUE | |
| `password` | VARCHAR(255) | bcrypt hash |
| `display_name` | VARCHAR(100) | |
| `avatar_url` | TEXT | MinIO URL |
| `role` | VARCHAR(20) | `user` \| `admin` |
| `is_active` | BOOLEAN | dùng cho ban/unban |
| `streak` | INTEGER | denormalized |
| `last_studied` | TIMESTAMPTZ | dùng tính reset streak |
| `created_at`, `updated_at` | TIMESTAMPTZ | trigger `set_updated_at()` |

Index: `email`, `role`, `is_active`.

### 3.2 `refresh_tokens` (migration 001)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `id` | UUID PK | |
| `user_id` | UUID FK → users, CASCADE | |
| `token` | VARCHAR(512) UNIQUE | **SHA-256 hash**, không lưu plain text |
| `device`, `ip` | VARCHAR / INET | metadata thiết bị |
| `is_revoked` | BOOLEAN | |
| `expires_at` | TIMESTAMPTZ | TTL 7 ngày |

Dọn token hết hạn: **Celery Beat task hằng ngày** (thay `pg_cron` — xem mục 1).

### 3.3 `folders` (migration 002)

`id, owner_id (FK CASCADE), name, description, created_at, updated_at`
Ràng buộc: `UNIQUE (owner_id, name)`.

### 3.4 `study_sets` (migration 002)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `owner_id` | FK → users, CASCADE | |
| `folder_id` | FK → folders, **SET NULL** | xóa folder không xóa set |
| `title`, `description` | | |
| `tags` | TEXT[] | GIN index |
| `is_public` | BOOLEAN | |
| `card_count` | INTEGER | denormalized, tự update qua trigger |
| `cloned_from` | FK → study_sets, SET NULL | |
| `fts_vector` | TSVECTOR GENERATED STORED | weight A=title, B=description, dùng `pg_trgm`/`unaccent` |

Trigger `update_card_count()`: `INSERT`/`DELETE` trên `cards` → `+1`/`-1` `card_count` tương ứng.

### 3.5 `cards` (migration 002)

`id, study_set_id (FK CASCADE), owner_id (FK CASCADE), front, back, image_url, "order" FLOAT, created_at, updated_at`

- `order` dùng **FLOAT** để reorder chỉ cần update 1 row (xem mục 10).
- `embedding vector(1536)` — **chưa bật**, để dành V2 (pgvector semantic search).
- Index: `(study_set_id, "order")`, `owner_id`.

### 3.6 `study_progress` (migration 003)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `user_id`, `card_id`, `study_set_id` | FK CASCADE | |
| `mode` | VARCHAR(20) | `flashcard \| learn \| test \| match` |
| `interval` | INTEGER | SM-2 |
| `ease_factor` | FLOAT, CHECK ≥ 1.3 | SM-2 |
| `streak` (repetitions) | INTEGER | |
| `next_review`, `last_reviewed` | TIMESTAMPTZ | |

Ràng buộc: `UNIQUE (user_id, card_id, mode)` — 1 card có **nhiều row progress**, mỗi mode 1 row riêng.

> ⚠️ **Khác biệt so với thiết kế gốc:** thiết kế gốc có cột `status VARCHAR(20) CHECK (status IN ('not_started','learning','known'))` lưu trực tiếp trong bảng. Thực tế triển khai **không lưu cột này trong DB** — `status` được **derive tại runtime** từ `interval` (`interval >= known_threshold_days` → `known`, ngược lại → `learning`; chưa có row progress → `not_started`). Lý do: tránh phải đồng bộ 2 nguồn sự thật (`interval` và `status`) mỗi lần update SM-2.

### 3.7 `study_sessions` (migration 003, append-only)

`id, user_id (FK CASCADE), study_set_id (FK CASCADE), mode, cards_studied, correct, incorrect, created_at, ended_at (NULL = đang mở)`

`duration_seconds` tính runtime = `ended_at - created_at`, không lưu cột riêng.

### 3.8 `session_answers` (migration 003, append-only, snapshot)

`id, session_id (FK CASCADE), user_id, card_id, front, back (snapshot tại thời điểm trả lời), user_answer, quality (1-5, nullable), is_correct, time_spent (ms), answered_at`

### 3.9 `set_clones` (migration 003, analytics only)

`id, original_set_id, original_owner_id, cloned_set_id, cloned_by, cloned_at`
Ràng buộc: `UNIQUE (original_set_id, cloned_by)` — 1 user chỉ clone 1 set gốc 1 lần (tính theo bản ghi analytics).

### 3.10 `system_config` (migration 004 — B.6)

Bảng single-row (`id = 1`), 7 field typed. Xem chi tiết mục 8.

### Trigger chung

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```
Áp dụng cho mọi bảng có `updated_at`.

### Quy tắc Cascade

| Quan hệ | Hành vi |
|---|---|
| Xóa `user` | CASCADE toàn bộ dữ liệu liên quan (tokens, folders, sets, cards, progress, sessions...) |
| Xóa `folder` | **SET NULL** `folder_id` trên `study_sets` — set không bị xóa |
| Xóa `study_set` | CASCADE `cards` |
| Xóa `card` | CASCADE `study_progress`, `session_answers` liên quan |

### pgvector — chuẩn bị cho V2 (chưa dùng ở V1)

```sql
ALTER TABLE cards ADD COLUMN embedding vector(1536);
CREATE INDEX idx_cards_embedding ON cards USING hnsw (embedding vector_cosine_ops);
```

---

## 4. Quy ước API chung

**Base URL:** `/api/v1` · **Auth:** JWT Bearer · **Format:** JSON · **Tổng:** 40 endpoints

### Response format — thực tế KHÔNG đồng nhất 100%

> ⚠️ **Khác biệt quan trọng so với thiết kế gốc:** thiết kế gốc quy định toàn bộ response theo envelope thống nhất `{ success, data, pagination }`. Thực tế implement:
> - Chỉ **5 endpoint Auth** (`register`, `login`, `refresh`, `logout`, `logout-all`) bọc `SuccessEnvelope[T]` = `{"success": true, "data": {...}}` (sửa ở Phase 10.1 để type generation đúng schema).
> - **Tất cả endpoint còn lại trả trực tiếp schema**, không bọc `success/data`. Ví dụ `GET /users/me` trả thẳng `UserProfile`.
> - Format phân trang **không đồng nhất** giữa các nhóm — xem bảng dưới.

**Phân trang theo nhóm:**

| Nhóm | Field phân trang |
|---|---|
| Cards | `items, total, page, page_size` |
| Sessions history | `items, total, page, limit` |
| Admin lists | theo từng endpoint riêng |

**Error format** (chuẩn `HTTPException` của FastAPI):
```json
{ "detail": "Error message" }
```
hoặc dạng có cấu trúc hơn (ví dụ auth):
```json
{ "detail": { "success": false, "error": { "code": "REGISTRATION_DISABLED", "message": "..." } } }
```

### Authentication

- **Access token**: JWT, header `Authorization: Bearer <token>`, TTL **15 phút**
- **Refresh token**: opaque random string, gửi qua **request body** (không phải cookie), lưu **hash SHA-256** trong DB, TTL 7 ngày
- **Rotation**: mỗi lần refresh, token cũ bị revoke, cấp cặp mới hoàn toàn

### Nguyên tắc bảo mật chung áp dụng xuyên suốt

- Mọi lookup theo quyền sở hữu (`get_by_id` cho folder/set/card...) trả **`None` thống nhất** cho cả "không tồn tại" lẫn "không đủ quyền" → luôn trả `404`, tránh **leak thông tin ownership**.
- `authenticate_user` trả `None` thống nhất cho sai email / sai password / user bị ban → tránh **user enumeration**.
- Login với account bị ban trả **cùng message** `"Email or password is incorrect"` như sai password — cố ý không lộ trạng thái tài khoản.

---

## 5. API Reference — User

### 5.1 Authentication — `/auth` (5 endpoints)

| Method | Path | Response |
|---|---|---|
| POST | `/auth/register` | 201, `SuccessEnvelope[RegisterResponse]` |
| POST | `/auth/login` | 200, `SuccessEnvelope[LoginResponse]` |
| POST | `/auth/refresh` | 200, `SuccessEnvelope[RefreshResponse]` |
| POST | `/auth/logout` | 200, `SuccessEnvelope[MessageData]` |
| POST | `/auth/logout-all` | 200, `SuccessEnvelope[MessageData]` |

- `register`: check `config.allow_registration` trước (403 `REGISTRATION_DISABLED` nếu tắt) → check email trùng (409 `EMAIL_TAKEN`) → bcrypt hash.
- `login`/`register` trả `{ user, tokens }`.
- `refresh`: body `{ refresh_token }` → SHA-256 hash → validate còn hạn/chưa revoke/user active → revoke cũ, issue mới.
- `logout`: body `{ refresh_token }`, revoke đúng token đó.
- `logout-all`: revoke toàn bộ token của user (mọi thiết bị).

### 5.2 User Profile — `/users` (4 endpoints, trả trực tiếp schema)

| Method | Path | Response |
|---|---|---|
| GET | `/users/me` | 200, `UserProfile` |
| PATCH | `/users/me` | 200, `UserProfile` (partial update `display_name`/`avatar_url`, phải có ≥1 field) |
| PATCH | `/users/me/password` | 204 (verify `old_password` bcrypt trước khi hash password mới) |
| POST | `/users/me/avatar` | 200, `{ avatar_url, message }` |

Avatar: content-type `jpeg/png/webp/gif`, max `config.max_image_size_mb` (default 5MB), path `avatars/{user_id}/avatar.{ext}` (overwrite).

### 5.3 Folders — `/folders` (5 endpoints)

`GET/POST /folders` · `GET/PATCH/DELETE /folders/{id}`

- `name` unique theo `(owner_id, name)`, trùng → 409.
- `PATCH` dùng `model_dump(exclude_unset=True)` để phân biệt "không gửi field" vs "gửi null".
- `DELETE` không cascade sets (DB `SET NULL folder_id`).

### 5.4 Study Sets — `/sets` (6 endpoints)

`GET/POST /sets` · `GET/PATCH/DELETE /sets/{id}` · `POST /sets/{id}/clone`

- `GET /sets` query: `search` (FTS `plainto_tsquery("simple", ...)`, không stemming — phù hợp đa ngôn ngữ), `folder_id` (kết hợp được cả 2).
- `POST`: chặn 400 nếu đạt `config.max_sets_per_user`.
- `GET /{id}`: xem được nếu owner hoặc `is_public=true`; không đủ quyền → 404 (theo nguyên tắc mục 4).
- `PATCH`: `folder_id` có 3 case — không gửi = giữ nguyên; `null` = bỏ khỏi folder; UUID = chuyển (validate ownership).
- `POST /{id}/clone`: copy title/description/tags + toàn bộ cards; set mới `is_public=False, folder_id=None, cloned_from=original.id`; ghi `SetClone`; **1 transaction** (dùng `flush()` trước `commit()`).

### 5.5 Cards — `/sets/{set_id}/cards` (7 endpoints)

```
GET/POST /sets/{set_id}/cards
GET/PATCH/DELETE /sets/{set_id}/cards/{card_id}
PATCH /sets/{set_id}/cards/{card_id}/order
POST  /sets/{set_id}/cards/{card_id}/image
```

- `card_count` tự động qua DB trigger — **không** update tay.
- Card mới: `order = max(order) + 1.0` (append cuối). Chặn 400 nếu đạt `config.max_cards_per_set` (dùng luôn `card_count` có sẵn, không `COUNT(*)` lại).
- **Reorder FLOAT `order`** — chỉ update 1 row:

| Trường hợp | Công thức |
|---|---|
| Lên đầu | `next_order - 1.0` |
| Xuống cuối | `prev_order + 1.0` |
| Chèn giữa 2 card | `(prev_order + next_order) / 2.0` |
| Không có card nào | `1.0` |

  Rebalance tự động về `1.0, 2.0, 3.0, ...` khi `abs(diff) < 1e-9`. Validator: `prev_order < next_order` nếu cả 2 gửi, sai → 422.
- Image: `jpeg/png/webp`, max `config.max_image_size_mb`, path `card-images/{card_id}/image.{ext}` (overwrite), chỉ owner.

### 5.6 Study Sessions & SM-2 — `/sessions` (4 endpoints)

```
POST /sessions                → 201, tạo session + cards due
POST /sessions/{id}/answers   → 200, nộp đáp án + SM-2 upsert
POST /sessions/{id}/end       → 200, kết thúc + streak
GET  /sessions                → 200, lịch sử (page/limit + filter set_id/mode)
```

- `POST /sessions`: check owner hoặc set public → tạo `study_sessions` (`ended_at=NULL`) → lấy cards "due" (`next_review <= now()` hoặc chưa có progress; **fallback trả toàn bộ cards** nếu không card nào due).
- `POST /sessions/{id}/answers`: check session còn mở → `map_quality()` → lấy `StudyProgress` hiện tại → tính SM-2 mới → **upsert** `study_progress` → insert `session_answers` (snapshot front/back) → cập nhật counters.
- `POST /sessions/{id}/end`: `ended_at=now()`, tính `accuracy`, gọi `update_streak()`.
- `GET /sessions`: chỉ `ended_at IS NOT NULL`, JOIN lấy `set_title`, sort `ended_at DESC`.

Chi tiết SM-2 và streak: xem mục 7.

### 5.7 Statistics — `/stats` (3 endpoints)

```
GET /stats/overview          → streak, cards known/learning, total_sessions, study_time, sets_studied
GET /stats/sessions          → ?range=7d|30d|90d&group_by=day|week — zero-fill đủ ngày
GET /sets/{set_id}/stats     → nằm trên sets_router (đúng REST convention)
```

Lưu ý kỹ thuật: 1 card có nhiều `study_progress` (1 row/mode) → classify known/learning dùng subquery `max(interval)` per card, tránh đếm trùng.

---

## 6. API Reference — Admin

Tất cả yêu cầu `role = admin`, sai role → 403.

### 6.1 Dashboard
`GET /admin/dashboard?range=7d|30d|90d` — user/set/session metrics, DAU/MAU, 2 chart zero-fill.

### 6.2 User Management (4 endpoints)

| Endpoint | Mô tả |
|---|---|
| `GET /admin/users` | List + search + filter(`role`/`is_active`) + sort + pagination |
| `GET /admin/users/{id}` | Chi tiết + stats + devices (`refresh_tokens`) + 5 session gần nhất |
| `PATCH /admin/users/{id}` | Ban/unban, cấp/thu hồi admin, force reset password |
| `DELETE /admin/users/{id}` | Xóa cascade |

**Self-protection (đã test kỹ):**

| Cơ chế | Hành vi |
|---|---|
| Ban user | Tự động revoke toàn bộ `refresh_tokens` |
| Admin tự ban/thu hồi quyền/xóa chính mình | 400 |
| `PATCH` body rỗng `{}` | 400 |
| Force reset password | `secrets.token_urlsafe(9)` + bcrypt hash + revoke hết token |

### 6.3 Study Set Management (3 endpoints)

`GET /admin/sets` (kể cả private, filter `owner_id`/`is_public`, sort `session_count`/`clone_count`) · `PATCH /admin/sets/{id}` (toggle `is_public`) · `DELETE /admin/sets/{id}` (cascade).

### 6.4 Statistics (3 endpoints)

| Endpoint | Nội dung |
|---|---|
| `GET /admin/stats/users` | growth chart, `streak_distribution` (4 bucket), `churn_rate` (>30 ngày) |
| `GET /admin/stats/learning` | sessions_chart, mode_distribution, avg_known_rate, avg_accuracy |
| `GET /admin/stats/content` | top 10 sets by sessions/clones, popular_tags (`func.unnest()` trên `tags`) |

### 6.5 System Config (2 endpoints)

`GET /admin/config` · `PATCH /admin/config` (update 1+ field). Chi tiết field: mục 8.

---

## 7. SM-2 Spaced Repetition Engine

Thuần logic, **không đụng DB** (`sm2_service.py`). Từ B.6, 3 hằng số đọc động từ `SystemConfig` thay vì hardcode.

| Kết quả | Công thức |
|---|---|
| Đúng (`quality ≥ 3`) | `new_ef = max(min_ease_factor, ef + 0.1 - (5 - q) * 0.08)`<br>`new_interval = round(max(1, interval) * new_ef)` |
| Sai (`quality < 3`) | `new_ef = max(min_ease_factor, ef - 0.2)`; `interval = 1`; `repetitions = 0` |

`status` (runtime, không lưu DB): `interval >= known_threshold_days` → `known`, ngược lại → `learning`; chưa có progress → `not_started`.

`map_quality()`:

| Mode | Logic |
|---|---|
| `learn` | Dùng `explicit_quality` (1–5) user chọn, bắt buộc |
| `flashcard / test / match` | Auto-map: đúng → quality 4, sai → quality 1 |

### Streak (theo ngày UTC, không phải rolling 24h)

| Điều kiện | Hành động |
|---|---|
| `last_studied IS NULL` | `streak = 1` |
| `last == today` | Giữ nguyên |
| `last == today - 1` | `streak += 1` |
| `last < today - 1` | Reset `streak = 1` |

---

## 8. System Config (Runtime-configurable)

Bảng `system_config` (single-row, `id=1`), thêm ở **B.6** để mọi giới hạn có thể đổi qua admin API **không cần redeploy**.

| Field | Type | Default | Wire vào |
|---|---|---|---|
| `initial_ease_factor` | float | 2.5 | `sm2_service.calculate_sm2()` |
| `min_ease_factor` | float | 1.3 | `sm2_service.calculate_sm2()` |
| `known_threshold_days` | int | 7 | `sessions.py`, `stats_service.py`, `admin_service.py` (đồng bộ 3 nơi — trước B.6 mỗi nơi hardcode riêng, có thể lệch số liệu) |
| `max_sets_per_user` | int | 50 | `set_service.create()` → 400 nếu vượt |
| `max_cards_per_set` | int | 500 | `card_service.create_card()` (dùng `card_count` có sẵn) |
| `max_image_size_mb` | int | 5 | `minio_service.py` (avatar + card image) |
| `allow_registration` | bool | true | `auth_service.register_user()` → 403 nếu tắt |

Validation: `min_ease_factor` không được > `initial_ease_factor` → 400.

**Nguyên tắc thiết kế B.6:** mọi param mới đều **optional với default = hằng số cũ** → không breaking change. Mọi bước có regression test (config default → kết quả y hệt trước khi wire) + config-effect test (đổi config → kết quả đổi theo).

Helper chung: `config_service.get_current_config(db)` — trả **raw model**, khác `admin_service.get_config()` trả Pydantic schema cho API.

> ⚠️ **Lý do kỹ thuật:** service raise `HTTPException` trực tiếp (không dùng `ValueError`) vì các router (`sets.py`, `auth.py`) có sẵn `except ValueError` gắn cứng 1 status/code khác (404 cho sets, 409 `EMAIL_TAKEN` cho auth) — dùng `ValueError` cho lỗi config sẽ bị bắt nhầm route xử lý lỗi.

---

## 9. Type Sharing FE ↔ BE

```
FastAPI (Pydantic models)
    → /openapi.json  (auto-generated)
    → openapi-typescript
    → packages/types/api.d.ts
    → Next.js: import type { components } from "@repo/types"
```

- Package: **`@repo/types`** (không phải `@sle/types` như thiết kế gốc — xem mục 2).
- `packages/types/package.json` có script `generate:types` chạy `openapi-typescript http://localhost:8000/openapi.json -o ./api.d.ts` — cần backend đang chạy.
- npm workspaces symlink package ở **root** `node_modules/@repo/types` (do hoisting) — hành vi đúng, không phải lỗi.
- 5 endpoint auth dùng schema đặt tên tự động: `SuccessEnvelope_RegisterResponse_`, `SuccessEnvelope_LoginResponse_`, `SuccessEnvelope_RefreshResponse_`, `SuccessEnvelope_MessageData_` (`openapi-typescript` thay `[`, `]` bằng `_` vì TS identifier không cho ký tự này).
- `GET /sets/{set_id}/cards` dùng schema riêng `CardListResponse`.
- Chạy lại `npm run generate:types` mỗi khi backend đổi schema.

### `SuccessEnvelope[T]` — bổ sung ở Phase 10.1

Rà soát phát hiện 5 endpoint (4 auth + `list_cards`) trả `Record<string, never>` do thiếu/sai `response_model`. Giải pháp: thêm generic wrapper dùng chung.

```python
# app/schemas/common.py
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class SuccessEnvelope(BaseModel, Generic[T]):
    """Bọc response thành công theo format {success, data} thống nhất."""
    success: bool = True
    data: T

class MessageData(BaseModel):
    message: str
```

Và `CardListResponse` riêng cho `list_cards`:
```python
class CardListResponse(BaseModel):
    items: list[CardResponse]
    total: int
    page: int
    page_size: int
```

---

## 10. Quyết định kiến trúc & Gotcha quan trọng

Chỉ giữ lại các quyết định có ảnh hưởng lâu dài đến cách phát triển/maintain — bỏ toàn bộ lỗi cú pháp/import/Pylance vụn vặt đã fix.

| # | Vấn đề | Quyết định / Giải pháp |
|---|---|---|
| 1 | `pg_cron` không có trong image `pgvector/pgvector:pg16` | Thay bằng **Celery Beat task** dọn refresh token hết hạn |
| 2 | `TIMESTAMPTZ` không tồn tại trong SQLAlchemy | Dùng `DateTime(timezone=True)` |
| 3 | Migration `003_learning_tables` có `revision = "id_được_generate"` — placeholder tiếng Việt gõ nhầm khi tạo, nhưng đã khớp cả file lẫn DB thực tế | **Giữ nguyên, không sửa** — sửa sẽ đứt migration chain |
| 4 | Thiết kế gốc: response envelope thống nhất `{success, data}` toàn bộ API | Thực tế: chỉ 5 endpoint Auth bọc envelope; còn lại trả trực tiếp schema (xem mục 4) |
| 5 | Thiết kế gốc: `study_progress.status` là cột lưu DB | Thực tế: **derive runtime** từ `interval`, không lưu cột riêng (tránh 2 nguồn sự thật) |
| 6 | Thiết kế gốc: scope package `@sle/types` | Thực tế monorepo dùng scope `@repo/` → package là `@repo/types` |
| 7 | Reorder card bằng FLOAT `order` | Chỉ update **1 row** mỗi lần kéo thả; rebalance toàn bộ về số nguyên khi khoảng cách 2 giá trị < `1e-9` |
| 8 | Ownership check (folder/set/card) | Luôn trả `None` thống nhất cho "không tồn tại" và "không đủ quyền" → 404, **tránh leak ownership** |
| 9 | Auth check (login) | `authenticate_user` trả `None` thống nhất mọi lỗi (sai email/password/bị ban) → **tránh user enumeration**; ban user login trả cùng message với sai password |
| 10 | Lỗi config nên raise gì | `HTTPException` trực tiếp từ service, **không** dùng `ValueError` (routers có sẵn `except ValueError` gắn cứng status khác, dễ bắt nhầm) |
| 11 | `card_count`, `duration_seconds`, `status` (progress) | Đều tính **runtime/trigger**, không lưu trùng lặp trong nhiều cột — nguyên tắc chung: tránh denormalize khi không cần |

---

## 11. Việc còn lại — Phase 9 & 10.2

Backend (Phase 0–8 + B.6 + 10.1) đã hoàn thành, 40 endpoints, type-safe FE↔BE. Còn lại theo `SLE_V1_Task_Breakdown.md`:

| Phase | Nội dung |
|---|---|
| **9.1** | Auth pages (Login/Register), Zustand auth store, TanStack Query mutations, protected route middleware |
| **9.2** | Dashboard/Home — danh sách sets, streak, stats tóm tắt |
| **9.3** | Folder & Set management UI — CRUD, drag-drop, reorder |
| **9.4** | 4 Study modes UI — Flashcard, Learn (quality 1–5), Test, Match |
| **9.5** | Stats & History UI — progress chart, breakdown known/learning/not_started |
| **9.6** | Admin UI — dashboard, user/set management, config panel |
| **10.2** | E2E flow test: register → tạo set → học → xem stats; admin flow: ban user, content moderation |

Lệnh chuẩn bị dev đầy đủ:
```bash
cd apps/api && .venv\Scripts\activate && docker compose up -d && uvicorn app.main:app --reload --port 8000
cd apps/web && npm run dev
```
