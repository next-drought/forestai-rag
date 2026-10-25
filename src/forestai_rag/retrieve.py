"""Hybrid retrieval: vector + keyword, merged with reciprocal rank fusion."""
import json

import psycopg
from pgvector.psycopg import register_vector
from psycopg.rows import dict_row
from .config import DATABASE_URL, SETTINGS
from .embed import embed_texts

VECTOR_SQL = """SELECT chunk_id, source_id, section, text, metadata
FROM chunks WHERE (%(flt)s::jsonb = '{}'::jsonb OR metadata @> %(flt)s::jsonb)
ORDER BY embedding <=> %(q)s::vector LIMIT %(k)s"""
KEYWORD_SQL = """SELECT chunk_id, source_id, section, text, metadata
FROM chunks WHERE tsv @@ plainto_tsquery('english', %(t)s)
AND (%(flt)s::jsonb = '{}'::jsonb OR metadata @> %(flt)s::jsonb)
ORDER BY ts_rank(tsv, plainto_tsquery('english', %(t)s)) DESC LIMIT %(k)s"""


def retrieve(query: str, metadata_filter: dict | None = None) -> list[dict]:
    r = SETTINGS["retrieval"]
    flt = json.dumps(metadata_filter or {})
    qv = embed_texts([query], "RETRIEVAL_QUERY")[0]
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        register_vector(conn)
        v = conn.execute(VECTOR_SQL, {"q": qv, "k": r["top_k_vector"], "flt": flt}).fetchall()
        k = conn.execute(KEYWORD_SQL, {"t": query, "k": r["top_k_keyword"], "flt": flt}).fetchall()
    scores, rows = {}, {}
    for ranked in (v, k):
        for rank, row in enumerate(ranked):
            scores[row["chunk_id"]] = scores.get(row["chunk_id"], 0) + 1 / (60 + rank)
            rows[row["chunk_id"]] = row
    top = sorted(scores, key=scores.get, reverse=True)[: r["final_k"]]
    return [rows[i] | {"score": scores[i]} for i in top]
