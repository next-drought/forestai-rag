# forestai-rag

Gemini RAG over forest-health data (oak wilt, USDA FIA/FHM, ForestAI documents), with pgvector first and an ADK agent on top.

Status: scaffold only. Nothing here has been run against a cloud project. Set credentials in `.env` (copy `.env.example`) before running.

## Layout
- `config/settings.yaml`: models, chunking, retrieval settings
- `sql/001_schema.sql`: pgvector + PostGIS schema
- `src/forestai_rag/`: ingest, chunk, embed, index, retrieve, generate
- `agent/forestai_agent/`: ADK agent skeleton (search, SQL and spatial tools)
- `eval/`: golden question set template and eval runner
- `docs/DEPLOY.md`: Cloud Run + Cloud SQL deployment behind Firebase Hosting
- `docs/PLAN.md`: implementation plan and AI-ready checklist
- `docs/DATA_READINESS.md`: source inventory template

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # fill in values
docker compose up -d db         # local Postgres with pgvector + PostGIS
psql "$DATABASE_URL" -f sql/001_schema.sql
python scripts/run_ingest.py data/raw
python eval/run_eval.py
adk web agent                    # try the agent locally
```
