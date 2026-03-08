# Phishing Hunter Backend

FastAPI backend for Zero-Day UI Phishing Hunter.

## What Is Implemented
- API versioning on `/api/v1`
- Auth endpoints:
  - `POST /api/v1/auth/register`
  - `POST /api/v1/auth/login`
  - `GET /api/v1/auth/me`
  - `PATCH /api/v1/auth/users/{id}/role` (admin only)
- Scan endpoints (`create/list/get/update/delete`)
- Result endpoints with scan existence validation
- Feedback endpoints with result existence validation
- Whitelist endpoints:
  - `POST /api/v1/whitelist`
  - `GET /api/v1/whitelist/check?domain=...`
- Hash similarity endpoint:
  - `POST /api/v1/hash-check`
- Brands endpoints:
  - `GET /api/v1/brands`
  - `GET /api/v1/brand/{id}`
  - `POST /api/v1/brand`
  - `PUT /api/v1/brand/{id}`
  - `DELETE /api/v1/brand/{id}`
- CORS support via env vars
- Health endpoint `GET /health`
- Async SQLAlchemy (SQLite locally, PostgreSQL in Docker)
- Alembic migration setup with initial schema revision
- Redis caching for hash-check requests
- Celery app + worker tasks wiring (`analyze_screenshot`, `check_logo`, `compute_risk`)
- Docker setup for `api + worker + postgres + redis + rabbitmq`
- Basic API tests using `pytest + httpx`
- CI workflow on GitHub Actions (`ruff` + `pytest`)
- Write endpoints protected with JWT bearer token
- Roles enabled (`admin`, `analyst`) with admin-only brand management
- Redis-backed rate limiting for sensitive write/auth endpoints

## Quick Local Run (current backend work)
```bash
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

API docs:
- `http://127.0.0.1:8000/docs`

Default local DB file: `phishing_v2.db`

## Docker Run (integration phase)
Use this when starting integration with AI/Extension teams and shared infra:
```bash
docker compose up --build
```

Migrations run automatically when the API container starts.

Services:
- API: `http://localhost:8000`
- Celery worker: running in `phishing-worker`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- RabbitMQ: `localhost:5672` (UI `http://localhost:15672`)

## Test
```bash
pytest -q
```

## Lint
```bash
ruff check .
```

## Auth Notes
- Use `POST /api/v1/auth/login` to get a bearer token.
- Send `Authorization: Bearer <token>` for write endpoints (`POST/PUT/DELETE`).
- First registered user becomes `admin`; next users are `analyst` by default.

## Backend Roadmap (what to do next)
1. Freeze API contracts with extension/AI teams (`/api/v1/*` payloads).
2. Replace placeholder Celery task logic with full ML/vision pipeline calls.
3. Add rate limiting and role-based authorization.
4. Add observability stack (structured logs, metrics, tracing).
