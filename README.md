# Gel MCP server

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=gel&config=eyJjb21tYW5kIjoidXZ4IC0tcmVmcmVzaCAtLWRpcmVjdG9yeSAuIC0tZnJvbSBnaXQraHR0cHM6Ly9naXRodWIuY29tL2dlbGRhdGEvZ2VsLW1jcC5naXQgZ2VsLW1jcCJ9)

This server is meant to help LLM-powered agents use advanced Gel features. 
It serves code and natural language examples that can be composed together to form a feature implementation.

## Usage in Cursor

1. We recommend using the MCP server alongside the Gel Rules for AI file. Add it to your project's `.cursor/rules` directory.
2. To configure the server, add the following configuration to `.cursor/mcp.json`:

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
                "gel-mcp"
            ]
        }
    }
}
```

3. Toggle the server on in **Cursor Settings** -> **MCP**
