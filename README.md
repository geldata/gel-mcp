# MCP server for EdgeDB

A Model Context Protocol server that enables LLMs to instrospect schemas and execute read-only queries in EdgeDB.

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
      "edgedb": {
          "command": "uvx",
          "args": ["edgedb-mcp"],
          "env": {
              "EDGEDB_DSN": "edgedb://user:pass@host:port/branch"
          }
        }
    }
}
```

The file itself can be located in the settings menu or in these directories:

- On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

For more information about connection strings see [DSN specification](https://docs.edgedb.com/database/reference/dsn) in EdgeDB's docs.

## Development

In order to set up the dev environment, begin by cloning the repo:

```bash
git clone https://github.com/edgedb/edgedb-mcp.git
```

... and running `uv sync`:

```bash
cd edgedb_mcp && uv sync
```

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/andrey/local/projects/mcp_server_built/edgedb-mcp run edgedb-mcp
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.
