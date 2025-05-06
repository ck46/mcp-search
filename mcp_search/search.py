"""Similarity search utilities."""

from __future__ import annotations

from typing import Any, List

from sqlalchemy import text as sa_text
from sqlmodel import select

from .db import async_session
from .models import MCPServer

__all__ = ["search_by_text"]


WEIGHTS: dict[str, float] = {
    "similarity": 0.6,
    "popularity": 0.2,
    "latency": 0.2,
}


async def search_by_text(query: str, k: int = 10) -> List[dict[str, Any]]:
    """Return the *k* most relevant servers for *query* sorted by *score*."""

    from .embedder import embed  # Local import to avoid a circular dependency.

    vector = await embed(query)

    stmt = sa_text(
        """
        SELECT *,
           (1 - embedding <#> :vec)  * :w_sim
           + popularity * :w_pop
           + (1.0 / NULLIF(latency_ms,0)) * :w_lat AS score
        FROM mcpserver
        ORDER BY score DESC
        LIMIT :k
        """
    )

    async with async_session() as session:
        rows = (
            await session.execute(
                stmt,
                {
                    "vec": vector,
                    "k": k,
                    "w_sim": WEIGHTS["similarity"],
                    "w_pop": WEIGHTS["popularity"],
                    "w_lat": WEIGHTS["latency"],
                },
            )
        ).mappings()
        return [dict(r) for r in rows] 