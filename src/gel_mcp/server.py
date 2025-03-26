from mcp.server import FastMCP
from pathlib import Path
import gel
import argparse

from gel_mcp.common.types import MCPExample


mcp = FastMCP("gel-mcp")
gel_client = gel.create_async_client()


parser = argparse.ArgumentParser()
parser.add_argument(
    "--workflows-file", type=Path, required=False, help="Path to workflows.jsonl"
)
args = parser.parse_args()

if args.workflows_file:
    from gel_mcp.import_from_workflows import import_from_workflows

    mcp_examples = import_from_workflows(args.workflows_file)
else:
    examples_path = Path(__file__).parent / ("mcp_examples.jsonl")
    if not examples_path.exists():
        raise FileNotFoundError(f"Missing examples file: {examples_path.as_posix()}")
    mcp_examples = [
        MCPExample.model_validate_json(line) for line in examples_path.open("r")
    ]


@mcp.tool("example://list")
async def list_examples() -> list[str]:
    """List all available code and workflow examples and their slugs"""
    return [f"<{e.slug}> {e.name}: {e.description}" for e in mcp_examples]


@mcp.tool("example://fetch")
async def fetch_example(slug: str) -> str | None:
    """Fetch a code or workflow example by its slug"""
    return next((e.to_markdown() for e in mcp_examples if e.slug == slug), None)


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
