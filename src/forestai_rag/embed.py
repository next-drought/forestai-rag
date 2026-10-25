from google import genai
from google.genai import types
from .config import SETTINGS

_client = None


def client():
    global _client
    if _client is None:
        _client = genai.Client()   # reads GOOGLE_GENAI_USE_VERTEXAI / project / location from env
    return _client


def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    m = SETTINGS["models"]
    out = []
    for i in range(0, len(texts), 50):
        res = client().models.embed_content(
            model=m["embedding"],
            contents=texts[i:i + 50],
            config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=m["embedding_dim"]),
        )
        out.extend(e.values for e in res.embeddings)
    return out
