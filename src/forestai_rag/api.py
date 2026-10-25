"""HTTP API for the ForestAI frontend. Every /api route requires a Firebase ID token."""
import os

import firebase_admin
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import auth
from pydantic import BaseModel, Field

from .generate import answer

firebase_admin.initialize_app()   # uses Cloud Run service account / ADC; project from GOOGLE_CLOUD_PROJECT

app = FastAPI(title="forestai-rag")
# Only needed when the frontend calls the Cloud Run URL directly; the Hosting rewrite is same-origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "https://forestai-platform.web.app,http://localhost:5173").split(","),
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


def current_user(authorization: str = Header(default="")) -> dict:
    # Local testing only; ignored on Cloud Run (K_SERVICE is always set there).
    if os.getenv("AUTH_DISABLED") == "1" and not os.getenv("K_SERVICE"):
        return {"uid": "local-dev"}
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing bearer token")
    try:
        return auth.verify_id_token(authorization.removeprefix("Bearer "))
    except Exception:
        raise HTTPException(401, "invalid token")


class QueryIn(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    filters: dict[str, str] = {}


class Source(BaseModel):
    n: int
    source_id: str
    section: str


class QueryOut(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/api/query", response_model=QueryOut)
def query(body: QueryIn, user: dict = Depends(current_user)):
    return answer(body.question, body.filters or None)
