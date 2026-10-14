# DocFlow AI

DocFlow AI is a portfolio-grade application for AI-powered invoice extraction, deterministic validation, human review, and evaluation.

## Architecture

- `frontend/` — Next.js App Router UI (upload, dashboard, review, history, evaluation)
- `backend/` — FastAPI REST API, PDF/OCR processing, extraction providers, PostgreSQL persistence
- `docker-compose.yml` — PostgreSQL, backend, and frontend services for local development

Uploaded PDFs are stored on disk (not in PostgreSQL). The API serves files through `/api/documents/{id}/file` with path traversal protections.

## Prerequisites

- Docker and Docker Compose
- Node.js 22+ (optional for local frontend dev)
- Python 3.12+ (optional for local backend dev)

## How to run and verify

### Option A — Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Open **http://localhost:3000** (not 8000 — that is the API only).

Quick checks:

- http://localhost:8000/api/health → `{"status":"ok"}`
- Upload `backend/evaluation/fixtures/pdfs/acme_001.pdf` → review page should show the PDF on the left within a few seconds

### Option B — Local dev (two terminals)

**Terminal 1 — backend**

```bash
docker compose up -d db   # Postgres on localhost:5433
cd backend && source .venv/bin/activate
export DATABASE_URL=postgresql+psycopg://docflow:docflow@localhost:5433/docflow
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend**

```bash
cd frontend
export NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Open **http://localhost:3000**. If you see “This site can’t be reached”, the dev server is not running or you opened the wrong port.

## Quick start (Docker)

1. Copy environment placeholders:

```bash
cp .env.example .env
```

2. Start the stack:

```bash
docker compose up --build
```

3. Open the app:

- Frontend: http://localhost:3000
- Backend health: http://localhost:8000/api/health

On startup, the backend applies Alembic migrations, generates synthetic evaluation fixtures, and runs the demo evaluation report.

## Demo mode (default)

Set in `.env`:

```env
EXTRACTION_PROVIDER=demo
```

Demo mode uses a deterministic extractor (labeled clearly in the UI/API). No paid API key is required.

Try bundled synthetic PDFs:

```bash
ls backend/evaluation/fixtures/pdfs
```

Upload `acme_001.pdf` through the UI or process it via API.

## LLM mode (optional)

```env
EXTRACTION_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

LLM failures are surfaced explicitly; the app does not silently fall back to fabricated success data.

## Local backend development

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env
# Ensure PostgreSQL is running and DATABASE_URL is set
alembic upgrade head
python scripts/generate_fixtures.py
python scripts/run_evaluation.py
uvicorn app.main:app --reload --port 8000
```

## Local frontend development

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Evaluation harness

Run reproducible fixture evaluation (demo provider):

```bash
cd backend
source .venv/bin/activate
python scripts/run_evaluation.py
```

Report output:

- `backend/evaluation/fixtures/reports/latest_evaluation.json`

API summary endpoint:

- `GET /api/evaluation/summary`

The dataset currently includes 12 synthetic invoices with ground-truth JSON. This is a portfolio benchmark, not proof of real-world accuracy.

## Testing

Backend:

```bash
cd backend
source .venv/bin/activate
export TEST_DATABASE_URL=postgresql+psycopg://docflow:docflow@localhost:5432/docflow_test
createdb docflow_test  # once
pytest
```

Frontend:

```bash
cd frontend
npm test
npm run build
```

## Main workflow

1. Upload PDF (`POST /api/documents`)
2. Process (`POST /api/documents/{id}/process`)
3. Review fields (`PUT /api/documents/{id}/review`)
4. Approve/reject
5. Export JSON/CSV

## Security notes (portfolio scope)

This demo is single-user and does not include authentication, tenant isolation, retention policies, or production deployment hardening. Do not use it for sensitive financial documents without additional controls.

## Known limitations

- Synchronous processing (no background worker queue)
- OCR quality depends on local Tesseract availability
- Evaluation metrics are computed on synthetic fixtures in demo mode
- LLM extraction quality depends on provider configuration and invoice layout
