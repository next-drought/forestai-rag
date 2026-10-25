"""Ingest: parse files, attach provenance, chunk, embed, write to Postgres."""
import hashlib
from pathlib import Path
import psycopg
from pgvector.psycopg import register_vector
from pypdf import PdfReader
from .chunk import chunk_text
from .config import DATABASE_URL, SETTINGS
from .embed import embed_texts


def read_file(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return "\n\n".join(p.extract_text() or "" for p in PdfReader(str(path)).pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def ingest_dir(root: str, license_note: str = "UNKNOWN - verify before publishing"):
    c = SETTINGS["chunking"]
    with psycopg.connect(DATABASE_URL) as conn:
        register_vector(conn)
        for path in sorted(Path(root).rglob("*")):
            if path.suffix.lower() not in {".md", ".txt", ".pdf"}:
                continue
            text = read_file(path)
            digest = hashlib.sha256(text.encode()).hexdigest()
            sid = path.stem
            conn.execute(
                "INSERT INTO sources(source_id,title,license,checksum) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT (source_id) DO UPDATE SET checksum=EXCLUDED.checksum",
                (sid, path.name, license_note, digest),
            )
            conn.execute("DELETE FROM chunks WHERE source_id=%s", (sid,))
            chunks = chunk_text(text, c["target_tokens"], c["overlap_tokens"], {"data_type": "document"})
            vecs = embed_texts([ch.text for ch in chunks])
            for ch, v in zip(chunks, vecs):
                conn.execute(
                    "INSERT INTO chunks(source_id,section,page,text,metadata,embed_model,embedding) "
                    "VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s)",
                    (sid, ch.section, ch.page, ch.text, __import__("json").dumps(ch.metadata),
                     SETTINGS["models"]["embedding"], v),
                )
            print(f"{path.name}: {len(chunks)} chunks")
