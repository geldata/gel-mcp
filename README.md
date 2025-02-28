# MCP server for Gel

A Model Context Protocol server that enables LLMs to instrospect schemas and execute read-only queries in Gel.

## Components

### Resources

This server introspects schema for object types discovered in the `default` module, as well as that module as a whole.
It does so using the following queries:

For the `default` module:

```edgeql
describe module default as sdl;
```

For individual types:

```edgeql
select (introspect Type) {
    name,
    properties: {
        name,
        target: {
            name
        }
    },
    links: {
        name,
        target: {
            name
        }
    }
};
```

Note that Claude is also capable of writing and executing introspection queries on its own.

### Tools

- `query`: Execute read-only EdgeQL queries against the connected database
    - Input: edgeql (string) 

## How to use with Claude Desktop

To use this server with the Claude Desktop app, add the following configuration to the "mcpServers" section of your claude_desktop_config.json:

```json
{
    "mcpServers": {
      "gel": {
          "command": "uvx",
          "args": ["gel-mcp"],
          "env": {
              "GEL_DSN": "gel://user:pass@host:port/branch"
          }
        }
    }
}
```

Note: on local, it needs DSN acquired via `gel instance credentials --insecure-dsn` and `?tls_security=insecure` at the end.


The file itself can be located in the settings menu or in these directories:

- On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

For more information about connection strings see [DSN specification](https://docs.geldata.com/database/reference/dsn) in Gel's docs.

## Development

In order to set up the dev environment, begin by cloning the repo:

```bash
git clone https://github.com/geldata/gel-mcp.git
```

... and running `uv sync`:

```bash
cd gel-mcp && uv sync
```

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory path/to/gel-mcp run gel-mcp
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
