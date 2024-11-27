import asyncio

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

import edgedb
from jinja2 import Template
import json

transaction_options = edgedb.TransactionOptions(readonly=False)
edgedb_client = edgedb.create_async_client().with_transaction_options(
    transaction_options
)


server = Server("edgedb-mcp")


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """

    type_names_query = """
        with module schema,
            types := (
                select ObjectType { name }
                filter .name like 'default::%'
            )
        select types.name;
        """

    async for tx in edgedb_client.transaction():
        async with tx:
            db_types = await tx.query_json(type_names_query)

    return [
        types.Resource(
            uri=AnyUrl(f"schema://{db_type}"),
            name=f"Type: {db_type}",
            description=f"Schema for {db_type} type",
            mimeType="application/json",
        )
        for db_type in db_types
    ]


@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """

    if uri.scheme != "schema":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    db_type = uri.path

    type_query = Template("""
        select (introspect {{ type }}) {
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
    """)

    async for tx in edgedb_client.transaction():
        async with tx:
            db_type = db_type.lstrip("/")
            db_type_info = await tx.query_json(type_query.render({"type": db_type}))

    return db_type_info


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """

    return [
        types.Tool(
            name="query",
            description="Run a read-only EdgeQL query",
            inputSchema={
                "type": "object",
                "properties": {
                    "edgeql": {"type": "string"},
                },
                "required": ["edgeql"],
            },
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """

    if name != "query":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    edgeql_query = arguments.get("edgeql")

    if not edgeql_query:
        raise ValueError("Missing EdgeQL query")

    async for tx in edgedb_client.transaction():
        async with tx:
            response = await tx.query_json(edgeql_query)

    # Notify clients that resources have changed
    await server.request_context.session.send_resource_list_changed()

    return [
        types.TextContent(
            type="text",
            text=f"{json.dumps(response)}",
        )
    ]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="edgedb-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
