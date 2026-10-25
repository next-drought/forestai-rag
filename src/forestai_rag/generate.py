"""Grounded answer generation with citations."""
from google.genai import types
from .config import SETTINGS
from .embed import client
from .retrieve import retrieve

SYSTEM = (
    "Answer only from the numbered context. Cite sources as [n]. "
    "If the context does not contain the answer, say you do not know. Do not use outside knowledge."
)


def answer(question: str, metadata_filter: dict | None = None) -> dict:
    hits = retrieve(question, metadata_filter)
    ctx = "\n\n".join(f"[{i+1}] ({h['source_id']} / {h['section']})\n{h['text']}" for i, h in enumerate(hits))
    res = client().models.generate_content(
        model=SETTINGS["models"]["generation"],
        contents=f"Context:\n{ctx}\n\nQuestion: {question}",
        config=types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.1),
    )
    return {"answer": res.text, "sources": [{"n": i + 1, "source_id": h["source_id"], "section": h["section"]} for i, h in enumerate(hits)]}
