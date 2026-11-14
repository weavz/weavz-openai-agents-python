from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from fixture.harness import CODE_EXAMPLE, FixtureServer, assert_fixture_result


def names_for(mode: str) -> set[str]:
    return {"demo__lookup_record"} if mode == "tools" else {"weavz_search", "weavz_read_api", "weavz_execute"}


async def exercise(mode: str, url: str, token: str, *, fixture: bool = False,
                   prompt: str | None = None) -> None:
    async with MCPServerStreamableHttp(
        name="Weavz", params={"url": url, "headers": {"Authorization": f"Bearer {token}"}}
    ) as server:
        tools = await server.list_tools()
        actual = {tool.name for tool in tools}
        if fixture and not names_for(mode).issubset(actual):
            raise RuntimeError(f"Expected fixture {mode} tools {sorted(names_for(mode))}; got {sorted(actual)}")
        if not fixture and prompt is None:
            print(json.dumps({"proof": "live Weavz MCP tool discovery", "mode": mode, "tools": sorted(actual)}))
            return
        if prompt:
            model = os.environ.get("WEAVZ_MODEL")
            if not model:
                raise RuntimeError("Set WEAVZ_MODEL and OPENAI_API_KEY for a model run")
            agent = Agent(name="Weavz assistant", instructions="Use the MCP tools to fulfill the request.", model=model, mcp_servers=[server])
            result = await Runner.run(agent, prompt)
            print(result.final_output)
            return
        if mode == "tools" and fixture:
            result = await server.call_tool("demo__lookup_record", {"recordId": "record-1"})
            assert_fixture_result(mode, result)
            results: Any = {"lookup": str(result)}
        elif fixture:
            search = await server.call_tool("weavz_search", {"query": "fixture"})
            read_api = await server.call_tool("weavz_read_api", {"alias": "demo", "action": "lookup_record"})
            result = await server.call_tool("weavz_execute", {"code": CODE_EXAMPLE})
            assert_fixture_result(mode, search)
            assert_fixture_result(mode, result)
            if isinstance(read_api, dict) and "demo" not in read_api.get("aliases", []):
                raise AssertionError(f"Unexpected demo API metadata: {read_api}")
            results = {"search": str(search), "read_api": str(read_api), "execute": str(result)}
        else:
            raise RuntimeError("A live tool call requires --prompt; use --fixture for synthetic calls")
        print(json.dumps({"proof": "local fixture adapter calls", "mode": mode, "tools": sorted(actual), "results": results}))


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", action="store_true")
    parser.add_argument("--mode", choices=("tools", "code"), default=os.getenv("WEAVZ_MCP_MODE", "tools"))
    parser.add_argument("--prompt")
    args = parser.parse_args()
    if args.fixture:
        if args.prompt:
            raise SystemExit("--prompt uses a model provider; run without --fixture for a live model run")
        with FixtureServer(args.mode) as fixture:
            fixture.reject_bad_token()
            await exercise(args.mode, fixture.url, "local-fixture-token", fixture=True)
    else:
        url, token = os.getenv("WEAVZ_MCP_URL"), os.getenv("WEAVZ_MCP_TOKEN")
        if not url or not token:
            raise SystemExit("Set WEAVZ_MCP_URL and WEAVZ_MCP_TOKEN from your custom Weavz MCP setup")
        if token.startswith("wvz_"):
            raise SystemExit("WEAVZ_MCP_TOKEN must be an MCP access token, not a Weavz REST API key")
        parsed = urlparse(url)
        if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise SystemExit("Use an HTTPS WEAVZ_MCP_URL except for a loopback development server")
        await exercise(args.mode, url, token, prompt=args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
