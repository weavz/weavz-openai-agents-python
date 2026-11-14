# OpenAI Agents SDK (Python) MCP integration examples with Weavz

<!-- weavz:discovery:start -->

Connect OpenAI Agents SDK (Python) to Slack, Gmail, GitHub and Notion through a remote Weavz Model Context Protocol (MCP) server. Use the native MCP adapter, then try the app setup recipes with your configured connections.

App setup recipes:

- [Slack MCP with OpenAI Agents SDK Python](docs/app-recipes.md#slack-mcp-with-openai-agents-sdk-python)
- [Gmail MCP with OpenAI Agents SDK Python](docs/app-recipes.md#gmail-mcp-with-openai-agents-sdk-python)
- [GitHub MCP with OpenAI Agents SDK Python](docs/app-recipes.md#github-mcp-with-openai-agents-sdk-python)
- [Notion MCP with OpenAI Agents SDK Python](docs/app-recipes.md#notion-mcp-with-openai-agents-sdk-python)

The framework consumes app tools from your configured Weavz MCP server. App recipes require your own app connections; automated checks use synthetic records.

[MCP app and framework directory](https://github.com/weavz/mcp-examples/blob/main/docs/integrations.md) · [All examples](https://github.com/weavz/mcp-examples) · [Weavz MCP guide](https://weavz.io/docs/guides/agent-framework-examples)

<!-- weavz:discovery:end -->

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
