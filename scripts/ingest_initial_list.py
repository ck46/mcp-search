#!/usr/bin/env python
"""Bootstrap the database with an initial list of MCP servers."""

from __future__ import annotations

import asyncio
import pathlib
import sys
from typing import List

from mcp_search.crawler import crawl_many

HERE = pathlib.Path(__file__).parent

DEFAULT_SERVERS_FILE = HERE.parent / "initial_servers.txt"


async def main(servers: List[str]) -> None:
    if not servers:
        print("[ingest] No servers to ingest.")
        return

    await crawl_many(servers)


if __name__ == "__main__":
    # Allow passing the servers file as the first CLI argument.
    servers_file = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SERVERS_FILE

    if not servers_file.exists():
        raise SystemExit(f"{servers_file} not found. Create the file with one URL per line.")

    servers_list = [l.strip() for l in servers_file.read_text().splitlines() if l.strip()]

    asyncio.run(main(servers_list)) 