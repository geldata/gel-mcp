from mcp.server import FastMCP
from pathlib import Path
import gel
import argparse
import shutil

from gel_mcp.import_from_workflows import import_from_workflows


mcp = FastMCP("gel-mcp")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--workflows-file", type=Path, required=False, help="Path to workflows.jsonl"
)
parser.add_argument(
    "--add-cursor-rules",
    action="store_true",
    help="Add Gel rules into the current project",
)

args = parser.parse_args()

if args.workflows_file:
    mcp_examples = import_from_workflows(args.workflows_file)
else:
    workflows_path = Path(__file__).parent / "static" / "workflows.jsonl"
    if not workflows_path.exists():
        raise FileNotFoundError(
            f"Missing default workflows file: {workflows_path.as_posix()}"
        )
    mcp_examples = import_from_workflows(workflows_path)


if args.add_cursor_rules:
    source_file = Path(__file__).parent / "static" / "gel-rules-auto.mdc"
    cursor_rules_dir = Path.cwd() / ".cursor" / "rules"
    cursor_rules_dir.mkdir(parents=True, exist_ok=True)
    dest_file = cursor_rules_dir / source_file.name
    if source_file.exists():
        shutil.copy2(source_file, dest_file)
    else:
        raise FileNotFoundError(f"Missing Gel rules file: {source_file.as_posix()}")


@mcp.tool()
async def list_examples() -> list[str]:
    """List all available code and workflow examples and their slugs"""
    return [f"<{e.slug}> {e.name}: {e.description}" for e in mcp_examples]


@mcp.tool()
async def fetch_example(slug: str) -> str | None:
    """Fetch a code or workflow example by its slug"""
    return next((e.to_markdown() for e in mcp_examples if e.slug == slug), None)


# @mcp.tool("schema://introspect")
# async def introspect_schema() -> str:
#     """Introspect the schema of the database configured in the project"""
#     return await gel_client.query("describe module default as sdl;")


@mcp.tool()
async def analyze_query(query: str) -> str:
    """Analyze a query to check for potential issues"""
    gel_client = gel.create_async_client()
    return await gel_client.query("analyze " + str(query))


@mcp.tool()
async def execute_query(query: str) -> str:
    """Execute a query and return the result"""
    gel_client = gel.create_async_client()
    return await gel_client.query(query)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
