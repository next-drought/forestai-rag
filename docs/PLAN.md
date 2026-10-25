# Plan: Gemini RAG on an AI-ready ForestAI dataset

## Architecture
- Ingest: raw files in Cloud Storage (versioned), parsed by a Python pipeline (Cloud Run job later). PDFs: Document AI Layout Parser or Gemini.
- Embed: Gemini embedding model; record model name and dimension on every chunk.
- Index: pgvector on Postgres (Cloud SQL or AlloyDB later) with PostGIS, so one query can combine vector, keyword, metadata and spatial filters. Then compare with Vertex AI RAG Engine and Vertex AI Vector Search.
- Retrieve: hybrid (vector + keyword) with reciprocal rank fusion, metadata filters, optional rerank.
- Generate: Gemini Flash by default, Pro for hard questions; grounded answers with citations.
- Agent: ADK agent with search_corpus, run_sql and spatial_query tools; add a critic sub-agent later.
- Serve: FastAPI on Cloud Run behind Firebase Auth.
- Observe: Cloud Logging callbacks, Cloud Trace, Vertex evaluation job.

## Phases (about 3 weeks part-time)
1. Days 1-3: data readiness. Finish docs/DATA_READINESS.md and write the 50-100 question golden set before retrieval code.
2. Days 4-8: baseline RAG (ingest, chunk, embed, pgvector, retrieve-then-generate). Record baseline scores.
3. Days 9-13: improve retrieval (chunk size and overlap, hybrid, rerank, query rewriting). Keep a metrics table.
4. Days 14-17: ADK agent with three tools and guardrail callbacks (refuse out-of-scope, require citations).
5. Days 18-21: deploy to Cloud Run with auth, eval gate in CI, README with architecture diagram and metrics.

## AI-ready and agent-ready checklist
Data
- [ ] Inventory sources with owner, update frequency and format
- [ ] Confirm licensing and terms of use (EDDMapS, USDA) before any public demo
- [ ] Remove personal, secret and location-sensitive data (exact coordinates on private land)
- [ ] Deduplicate; normalize units, dates, species names and coordinate reference systems
- [ ] Log missing values and quality issues next to the data
- [ ] Store source, version, retrieval date and checksum for every record

Documents and chunks
- [ ] Extract structure (headings, tables, captions)
- [ ] Chunk by section with overlap and a parent-document pointer
- [ ] Metadata per chunk: source, page, species, region, year, data type, access level
- [ ] Turn tables into text summaries; keep originals queryable by SQL
- [ ] Record embedding model and dimension; re-index on change

Retrieval and quality
- [ ] Golden question set with expected sources
- [ ] Track recall@k, groundedness, citation accuracy, refusal behavior
- [ ] Held-out test slice never used for tuning
- [ ] Incremental refresh job and a rule for removing stale chunks

Agent-readiness
- [ ] Typed tool signatures, clear docstrings, Pydantic input/output schemas
- [ ] Deterministic tools with timeouts, rate limits and clear errors
- [ ] Tools run under the end user's identity with least-privilege scopes; approval before writes
- [ ] Log every prompt, tool call and response with a trace ID
- [ ] Prompts and policies in versioned files
- [ ] Consider exposing corpus tools through an MCP server

Production
- [ ] Cost and latency budgets; cache repeated queries
- [ ] Prompt-injection tests against retrieved content
- [ ] User feedback loop for wrong answers
