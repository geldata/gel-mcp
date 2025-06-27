# Gel MCP server

This MCP server provides tools and resources that help coding agents use the Gel database.

## Available tools

1. `execute_query`: run a query against the Gel instance configured in the current project. Supports arguments and globals.
2. `try_query`: run a query in a transaction that gets rolled back in the end, preventing actual data modification.
3. `list_examples` and `fetch_example`: access code examples for advanced workflows such as configuring the AI extension.

## Development

```bash
uv sync
mcp dev src/gel_mcp/server.py
```

