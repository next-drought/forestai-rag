import sys
sys.path.insert(0, "src")
from forestai_rag.ingest import ingest_dir

ingest_dir(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
