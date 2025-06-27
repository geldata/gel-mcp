# Gel MCP server

This MCP server provides tools and resources that help coding agents use the Gel database.

## Available tools

1. `execute_query`: run a query against the Gel instance configured in the current project. Supports arguments and globals.
2. `try_query`: run a query in a transaction that gets rolled back in the end, preventing actual data modification.
3. `list_examples` and `fetch_example`: access code examples for advanced workflows such as configuring the AI extension.
4. `list_rules` and `fetch_rule`: in case you forgot to configure Gel rules in your text editor, the agent can access them like this, too.

## Install

If at any point you get lost, refer to [this repository](https://github.com/geldata/gel-ai-rules/tree/main/rendered) to see an example config layout for your editor.

### Cursor

Add the following to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "gel": {
      "command": "uvx",
      "args": [
        "--refresh",
        "--python",
        "3.13",
        "--directory",
        ".",
        "--from",
        "git+https://github.com/geldata/gel-mcp.git",
        "gel-mcp"
      ]
    }
  }
}
```

### Claude Code

Add the following to `.mcp.json`:

```json
{
  "mcpServers": {
    "gel": {
      "command": "uvx",
      "args": [
        "--refresh",
        "--python",
        "3.13",
        "--directory",
        ".",
        "--from",
        "git+https://github.com/geldata/gel-mcp.git",
        "gel-mcp"
      ]
    }
  }
}
```

### VSCode with Copilot

Add the following to `.vscode/mcp.json`:

```json
{
  "servers": {
    "gel": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--refresh",
        "--python",
        "3.13",
        "--directory",
        ".",
        "--from",
        "git+https://github.com/geldata/gel-mcp.git",
        "gel-mcp"
      ]
    }
  }
}
```

### Windsurf

Follow Windsurf Cascade's [documentation](https://docs.windsurf.com/windsurf/cascade/mcp#mcp-config-json) to open global `mcp_config.json` via the clicky interface.
Add the following:

```json
{
  "mcpServers": {
    "gel": {
      "command": "uvx",
      "args": [
        "--refresh",
        "--python",
        "3.13",
        "--directory",
        ".",
        "--from",
        "git+https://github.com/geldata/gel-mcp.git",
        "gel-mcp"
      ]
    }
  }
}
```

### Zed

Add the following to `.zed/settings.json`:

```json
{
  "context_servers": {
    "gel": {
      "source": "custom",
      "command": {
        "path": "uvx",
        "args": [
          "--refresh",
          "--python",
          "3.13",
          "--directory",
          ".",
          "--from",
          "git+https://github.com/geldata/gel-mcp.git",
          "gel-mcp"
        ],
        "env": {}
      }
    }
  }
}
```


## Develop

Clone the repository and create the virtual environment:

```bash
uv sync
```

Open the server in the MCP Inspector:

```bash
mcp dev src/gel_mcp/server.py
```

