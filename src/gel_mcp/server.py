from mcp.server import FastMCP
from pathlib import Path
import gel

from gel_mcp.common.types import CodeExample, WorkflowExample


mcp = FastMCP("gel-mcp")
gel_client = gel.create_async_client()


with (Path(__file__).parent / ("code_examples.jsonl")).open("r") as f:
    code_examples = [CodeExample.model_validate_json(line) for line in f]

with (Path(__file__).parent / ("workflow_examples.jsonl")).open("r") as f:
    workflow_examples = [WorkflowExample.model_validate_json(line) for line in f]


@mcp.tool("example://list")
async def list_examples() -> list[str]:
    """List all available code and workflow examples and their slugs"""
    return [f"{e.slug}: {e.description}" for e in code_examples + workflow_examples]


@mcp.tool("example://fetch")
async def fetch_example(slug: str) -> str | None:
    """Fetch a code or workflow example by its slug"""
    return next((e for e in code_examples + workflow_examples if e.slug == slug), None)


@mcp.tool("schema://introspect")
async def introspect_schema() -> str:
    """Introspect the schema of the database configured in the project"""
    return await gel_client.query("describe module default as sdl;")


@mcp.tool("query://analyze")
async def analyze_query(query: str) -> str:
    """Analyze a query to check for potential issues"""
    return await gel_client.query("analyze <str>$gel_query", gel_query=query)


@mcp.tool("query://execute")
async def execute_query(query: str) -> str:
    """Execute a query and return the result"""
    return await gel_client.query(query)


def main():
    mcp.run()


if __name__ == "__main__":
    main()