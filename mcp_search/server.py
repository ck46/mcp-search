"""Expose the search capabilities as an MCP server (FastAPI under the hood)."""

from __future__ import annotations

import asyncio

from mcp.server.fastmcp import FastMCP

from .db import init_db
from .search import search_by_text

__all__ = ["mcp"]

mcp = FastMCP("MCP-Search")


@mcp.resource("search://{query}")
async def search_resource(query: str):
    """Resource handler so users can *get* `search://<query>` URIs."""

    return await search_by_text(query)


@mcp.tool()
async def recommend(query: str):
    """Return a ranked list of servers for a text or JSON/YAML definition."""

    # In the MVP we simply forward the query to the text search, but one could
    # parse a YAML / JSON schema here to extract constraints.
    return await search_by_text(query)


async def _main() -> None:
    await init_db()
    mcp.run()


if __name__ == "__main__":
    asyncio.run(_main()) 