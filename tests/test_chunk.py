import sys
sys.path.insert(0, "src")
from forestai_rag.chunk import chunk_text


def test_sections_and_overlap():
    text = "# A\n\n" + "word " * 400 + "\n\n" + "next para " * 200 + "\n\n# B\n\nshort"
    chunks = chunk_text(text, target_tokens=100, overlap_tokens=10)
    assert len(chunks) >= 3
    assert {c.section for c in chunks} == {"A", "B"}
