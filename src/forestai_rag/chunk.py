"""Structure-aware chunking: split on headings, then paragraphs, with overlap."""
import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    section: str = ""
    page: int | None = None
    metadata: dict = field(default_factory=dict)


def _approx_tokens(s: str) -> int:
    return max(1, len(s) // 4)


def chunk_text(text: str, target_tokens=400, overlap_tokens=60, metadata=None) -> list[Chunk]:
    metadata = metadata or {}
    sections = re.split(r"(?m)^(#{1,4} .+)$", text)
    chunks, section = [], ""
    for part in sections:
        if re.match(r"^#{1,4} ", part):
            section = part.lstrip("# ").strip()
            continue
        buf = ""
        for para in [p.strip() for p in part.split("\n\n") if p.strip()]:
            if buf and _approx_tokens(buf + para) > target_tokens:
                chunks.append(Chunk(buf.strip(), section, metadata=dict(metadata)))
                tail = buf[-overlap_tokens * 4:]
                buf = tail + "\n\n" + para
            else:
                buf = (buf + "\n\n" + para) if buf else para
        if buf.strip():
            chunks.append(Chunk(buf.strip(), section, metadata=dict(metadata)))
    return chunks
