# Gel MCP server

This MCP server provides tools and resources that help coding agents use the Gel database.

Currently, only Cursor is officially supported. 
To get started with standard settings, click the button below:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=gel&config=eyJjb21tYW5kIjoidXZ4IC0tcmVmcmVzaCAtLWRpcmVjdG9yeSAuIC0tZnJvbSBnaXQraHR0cHM6Ly9naXRodWIuY29tL2dlbGRhdGEvZ2VsLW1jcC5naXQgZ2VsLW1jcCJ9)

**Warning**: activating the server with default settings in your current project will cause it to put multiple Gel rules files under `.cursor/rules`.
If you would like it to not do that, please use a custom command instead.

## Manual command

To configure the server, add the following configuration to `.cursor/mcp.json`:

```json
{
    "mcpServers": {
        "gel": {
            "command": "uvx",
            "args": [
                "--refresh",
                "--directory",
                ".",
                "--from",
                "git+https://github.com/geldata/gel-mcp.git",
                "gel-mcp",
                "--add-cursor-rules"
            ]
        }
    }
}
```

Afterwards, toggle the server on in **Cursor Settings** -> **MCP**.

## Available tools

1. `execute_query`: run a query against the Gel instance configured in the current project. Supports arguments and globals.
2. `try_query`: run a query in a transaction that gets rolled back in the end, preventing actual data modification.
3. `list_examples` and `fetch_example`: access code examples for advanced workflows such as configuring the AI extension.

In addition to that, the server automatically puts rules files for Gel, TS query builder and Python query builder + ORM into the current project's configuration.

