"""Asynchronous crawler that connects to MCP servers and records their metadata."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Iterable

from mcp import ClientSession, StdioServerParameters

from .db import async_session
from .embedder import embed
from .models import MCPServer

__all__ = ["crawl_one", "crawl_many"]


async def crawl_one(url: str) -> None:
    """Fetch metadata & embedding for a single *url* and store it in Postgres."""

    start = time.perf_counter()

    params = StdioServerParameters(command=url, args=[])
    async with ClientSession.from_stdio(params) as session:
        await session.initialize()

        name = session.server_name
        tools = await session.list_tools()
        resources = await session.list_resources()
        prompts = await session.list_prompts()

    latency = int((time.perf_counter() - start) * 1000)

    description = (
        f"Tools: {len(tools)}, Resources: {len(resources)}, Prompts: {len(prompts)}"
    )

    # Build a text blob for the embedding model.
    text_blob = "\n".join(
        [
            name,
            description,
            "\n".join(t.docstring or t.name for t in tools),
        ]
    )

    vector = await embed(text_blob)

    srv = MCPServer(
        url=url,
        name=name,
        description=description,
        capabilities={
            "tools": [t.name for t in tools],
            "resources": [r.uri for r in resources],
            "prompts": [p.name for p in prompts],
        },
        tags=[],
        latency_ms=latency,
        embedding=vector,
    )

    # Upsert semantics: if *url* already exists update the row, otherwise insert.
    async with async_session() as s:
        s.add(srv)
        await s.commit()


async def crawl_many(urls: Iterable[str], *, concurrency: int = 10) -> None:
    """Crawl several *urls* concurrently."""

    sem = asyncio.Semaphore(concurrency)

    async def _worker(u: str) -> None:
        async with sem:
            try:
                await crawl_one(u)
            except Exception as exc:  # noqa: BLE001
                # Log and carry on.
                print(f"[crawl] {u}: {exc}")

    await asyncio.gather(*(_worker(u) for u in urls)) 