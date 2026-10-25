"""Send a one-word prompt to each candidate model and report which ones this project can call."""
import os
import sys

from google import genai

DEFAULT = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash",
           "gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.1-pro-preview"]

client = genai.Client()
print("location:", os.environ.get("GOOGLE_CLOUD_LOCATION"))
try:
    client.models.embed_content(model="gemini-embedding-001", contents="ok")
    print("OK    gemini-embedding-001 (embedding)")
except Exception as e:
    print(f"FAIL  gemini-embedding-001 (embedding): {str(e)[:90]}")
for name in sys.argv[1:] or DEFAULT:
    try:
        client.models.generate_content(model=name, contents="Reply with OK.")
        print(f"OK    {name}")
    except Exception as e:
        print(f"FAIL  {name}: {str(e)[:90]}")
