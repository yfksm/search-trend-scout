# Search Trend Scout (MVP v1.0)

A specialized aggregation, summarization, and prioritization service designed for Search, IR, and RAG engineers. 

Search Trend Scout cuts through the noise of daily information overload by fetching recent articles and events, scoring them based on freshness and practical impact (e.g., benchmarking, architecture tradeoffs), and extracting the "Why Important" insight using LLM summarization.

## Architecture

This project is structured as a Dockerized modular application with 3 primary components:

- **Web (Next.js 15, React 19, Tailwind CSS v4)**: A premium, dark-mode focused UI with highly responsive SWR-backed optimistic updates.
- **API (FastAPI, Python 3.11+)**: Asynchronous Python backend managing ingestion cron loops, SQLite/Postgres interfacing, and endpoints.
- **DB (PostgreSQL)**: Stores feeds, items, user states (read/bookmarks), and tags.
- **LLM Summarizer**: An extensible abstraction over OpenAI's `gpt-4o-mini` (or similar providers) for metadata extraction and bullet generation.

## Prerequisites

- Docker and Docker Compose
- (Optional but recommended) OpenAI API Key for AI Summarization
- (Optional) Connpass API Key for Japanese Study Group events

## Setup & Running Locally

1. **Clone the repository** (if not already done).

2. **Configure Environment Variables**
   Create a `.env` file inside the `api/` directory (or map them in `docker-compose.yml`):
   ```env
   # api/.env
   LLM_PROVIDER=openai
   LLM_API_KEY=sk-your-openai-api-key-here
   CONNPASS_API_KEY=your-connpass-api-key-here
   ```
   *Note: Even without keys, the app will gracefully fallback to rule-based scraping and dummy summaries.*

3. **Start the Application**
   From the root of the project, run:
   ```bash
   docker compose up --build -d
   ```

4. **Verify Application**
   - **Frontend:** http://localhost:3000
   - **API Docs (Swagger):** http://localhost:8000/docs

5. **Trigger Ingestion (Initial Load)**
   You can trigger a feed ingestion via the UI ("Run Ingestion" button) or via a manual curl command:
   ```bash
   curl -X POST http://localhost:8000/api/ingest/run
   ```

## Development & Code Quality

This project enforces strict typing and formatting standards:

### Backend (Python)
- Handled via `ruff`. 
- To format: `cd api && ruff format . && ruff check --fix .`

### Frontend (TypeScript)
- Handled via `prettier` and Next.js `eslint`.
- To format: `cd web && npx prettier --write "src/**/*.{ts,tsx}"`

## Known Limitations (Phase 1 MVP)
- **Ingestion Execution:** Uses FastAPI `BackgroundTasks`. Not suited for heavy multi-worker scaling (Celery/Redis planned for Phase 2).
- **Authentication:** Currently single-user mode. User IDs are mocked globally or tied securely to a single local instance database.
