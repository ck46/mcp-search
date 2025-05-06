from __future__ import annotations

from typing import Optional, List

from pgvector.sqlalchemy import Vector
from sqlmodel import Field, SQLModel


class MCPServer(SQLModel, table=True):
    """A minimal representation of a public MCP server."""

    id: Optional[int] = Field(default=None, primary_key=True)

    # ── Basic metadata ────────────────────────────────────────────────────
    url: str = Field(index=True, unique=True)
    name: str
    description: str

    # ── Structured capabilities ──────────────────────────────────────────
    # Stored as JSONB in Postgres via the default SQLModel → SQLAlchemy mapping.
    capabilities: dict

    # Tags stored as a *text[]* array for easy filtering.
    tags: List[str] = Field(sa_column_kwargs={"type_": "text[]"})

    # ── Ranking signals ──────────────────────────────────────────────────
    latency_ms: int | None = None  # Average round-trip time in milliseconds.
    popularity: int = 0  # GitHub stars, manual votes, etc.

    # ── Embedding vector ──────────────────────────────────────────────────
    embedding: list[float] = Field(sa_column=Vector(dim=1536)) 