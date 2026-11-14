# OpenAI Agents SDK + Weavz MCP

This starter uses the Agents SDK's native `MCPServerStreamableHttp` adapter. Set up a custom Weavz MCP server in Tool Mode or Code Mode first. The mode is a server-side setting; `WEAVZ_MCP_MODE` validates the advertised tool names and cannot switch a remote server.

Requires Python 3.11 or 3.12 and uv. Set `WEAVZ_MCP_URL` to the Streamable HTTP URL and `WEAVZ_MCP_TOKEN` to its MCP access token. Do not use a Weavz REST API key. The personal `https://platform.weavz.io/mcp/weavz` server uses OAuth, not this bearer-token flow.

## Local fixture

```sh
uv sync --locked
uv run python main.py --fixture --mode tools
uv run python main.py --fixture --mode code
uv run pytest
```

This starts a separate local MCP SDK fixture, calls it through the OpenAI Agents MCP adapter, and shuts it down. The data is synthetic; no model or live Weavz call occurs.

## Your Weavz server

Copy `.env.example` to `.env`, set values from your custom server setup, then run `uv run --env-file .env python main.py --mode tools` or `--mode code` to discover the server's actual tools through the adapter. No demo alias is assumed on a live server.

For an optional agent run, connect an app containing records for your task, set `WEAVZ_MODEL` and `OPENAI_API_KEY`, then run `uv run --env-file .env python main.py --mode tools --prompt "Find the latest record matching the task you connected"`. The server connection stays open through the run and closes afterward.
