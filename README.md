# Prompt Gauge — MVP

Plain English in. Production‑grade prompts out. This MVP parses a natural language goal, explains it, generates 2 prompt styles, and logs runs.

## What is here
- **Frontend**: Next.js app with a single page to enter a goal and view Explain + Generate results.
- **Backend**: FastAPI with `/explain` and `/generate` endpoints. SQLite by default. Postgres optional.
- **Storage**: SQLAlchemy models for projects, prompts, versions, and runs.
- **Providers**: OpenAI adapter stub. Bring your own keys.

## Quick start

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Optional: copy .env.example to .env and set DATABASE_URL and provider keys.
uvicorn app:app --reload --port 8001
```

### 2) Frontend
```bash
cd ../frontend
npm i
npm run dev  # starts on http://localhost:3000
```

### 3) Use it
- Open http://localhost:3000
- Type a goal like: "Turn a messy meeting transcript into a 6‑bullet action list in JSON"
- Click Explain then Generate
- Toggle styles and copy the output

## Environment
- **SQLite default**: no setup needed. Creates `prompt_gauge.db` in backend folder.
- **Postgres**: set `DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/prompt_gauge` and ensure `CREATE EXTENSION IF NOT EXISTS vector;` if you add embeddings later.
- **OpenAI**: set `OPENAI_API_KEY`. The app will try the provider first and fall back to heuristics if unavailable.

## Notes
- This is a starter scaffold. Extend `services/generate.py` to add more styles and evals, and wire a proper run logger.
- For production, add auth, orgs, and a background worker for batch evals.
