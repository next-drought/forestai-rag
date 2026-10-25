"""ADK agent skeleton. Tools are typed and documented because ADK builds tool schemas from them."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import Agent

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from forestai_rag.retrieve import retrieve  # noqa: E402

load_dotenv()


def search_corpus(query: str, species: str = "", region: str = "") -> dict:
    """Search the forest-health document corpus.

    Args:
        query: Natural-language question.
        species: Optional species filter, e.g. 'Quercus virginiana'.
        region: Optional region filter, e.g. 'Texas'.

    Returns:
        A dict with 'results': list of {source_id, section, text}.
    """
    flt = {k: v for k, v in {"species": species, "region": region}.items() if v}
    hits = retrieve(query, flt)
    return {"results": [{"source_id": h["source_id"], "section": h["section"], "text": h["text"]} for h in hits]}


def run_sql(query: str) -> dict:
    """Run a read-only SQL query against the tabular forest-health tables.

    TODO: connect with a read-only database role, allow-list tables, enforce row and time limits.
    """
    return {"error": "not implemented"}


def spatial_query(lat: float, lon: float, radius_km: float = 25.0) -> dict:
    """Find records near a point. TODO: implement with PostGIS ST_DWithin on chunks.geom."""
    return {"error": "not implemented"}


root_agent = Agent(
    model=os.getenv("GEN_MODEL", "gemini-2.5-flash"),
    name="forestai_agent",
    description="Answers forest-health questions using the ForestAI corpus, with citations.",
    instruction=(
        "Use search_corpus for questions about forest health, oak wilt and related data. "
        "Cite the source_id for every claim. If tools return nothing relevant, say you do not know. "
        "Refuse questions outside forest health."
    ),
    tools=[search_corpus, run_sql, spatial_query],
)
