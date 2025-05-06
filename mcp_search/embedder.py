"""Thin wrapper around the OpenAI embeddings API."""

from __future__ import annotations

import openai

from .settings import settings

# Configure the client once at import time. All subsequent calls will re-use it.
openai.api_key = settings.OPENAI_API_KEY


async def embed(text: str) -> list[float]:
    """Return a 1536-dimensional embedding for *text* using the configured model."""

    response = await openai.Embedding.acreate(
        model=settings.EMBEDDING_MODEL,
        input=text,
    )
    # The v1 OpenAI client returns a *pydantic.BaseModel* so we can access attributes.
    return response.data[0].embedding  # type: ignore[attr-defined] 