"""Baseline eval: retrieval recall@k and fact coverage. Add an LLM judge for groundedness later."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
from forestai_rag.generate import answer  # noqa: E402

path = Path(sys.argv[1] if len(sys.argv) > 1 else "eval/golden_set.jsonl")
rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
hit = fact = n_src = n_fact = 0
for r in rows:
    out = answer(r["question"])
    got = {s["source_id"] for s in out["sources"]}
    if r["expected_sources"]:
        n_src += 1
        hit += bool(got & set(r["expected_sources"]))
    for f in r["expected_facts"]:
        n_fact += 1
        fact += f.lower() in out["answer"].lower()
print(f"recall@k: {hit}/{n_src}  fact coverage: {fact}/{n_fact}")
