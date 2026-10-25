"""List Gemini base models available to this project via Vertex AI."""
from google import genai

client = genai.Client()   # keep a reference; a temporary client gets closed mid-iteration
for m in client.models.list(config={"query_base": True}):
    if "gemini" in m.name:
        print(m.name)
