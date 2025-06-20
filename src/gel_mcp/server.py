from mcp.server.fastmcp import FastMCP
from pathlib import Path
import gel
import argparse
import shutil
import json
from typing import Any

from gel_mcp.import_from_workflows import import_from_workflows
from gel_mcp.common.types import MCPExample


mcp = FastMCP("gel-mcp")

WORKFLOWS_PATH = Path(__file__).parent / "static" / "workflows.jsonl"


def fetch_examples(workflows_path: Path) -> list[MCPExample]:
    """Load examples from workflows file."""
    if not workflows_path.exists():
        raise FileNotFoundError(
            f"Missing default workflows file: {workflows_path.as_posix()}"
        )
    return import_from_workflows(workflows_path)


@mcp.tool()
async def list_examples() -> list[str]:
    """List all available code and workflow examples and their slugs"""
    examples = fetch_examples(WORKFLOWS_PATH)
    return [f"<{e.slug}> {e.name}: {e.description}" for e in examples]


@mcp.tool()
async def fetch_example(slug: str) -> str | None:
    """Fetch a code or workflow example by its slug"""
    examples = fetch_examples(WORKFLOWS_PATH)
    return next((e.to_markdown() for e in examples if e.slug == slug), None)


@mcp.tool()
async def execute_query(
    query: str,
    arguments: dict[str, Any] | None = None,
    globals: dict[str, Any] | None = None,
) -> list[Any]:
    """Execute a query and return the result as JSON

    Args:
        query: The EdgeQL query to execute
        arguments: Optional dictionary of query parameters to pass to the query
        globals: Optional dictionary of global variables to pass to the query

    Returns:
        List containing the query result in JSON format
    """
    gel_client = gel.create_async_client()
    if globals:
        gel_client = gel_client.with_globals(**globals)

    if arguments:
        result = await gel_client.query_json(query, **arguments)
    else:
        result = await gel_client.query_json(query)

    if result is None:
        raise ValueError("Query returned None")

    parsed_result = json.loads(result)
    assert isinstance(parsed_result, list), (
        f"Expected list from query, got {type(parsed_result)}"
    )
    return parsed_result


@mcp.tool()
async def try_query(
    query: str,
    arguments: dict[str, Any] | None = None,
    globals: dict[str, Any] | None = None,
) -> list[Any]:
    """Execute a query in a transaction that gets rolled back, allowing you to test queries without making permanent changes

    Args:
        query: The EdgeQL query to execute
        arguments: Optional dictionary of query parameters to pass to the query
        globals: Optional dictionary of global variables to pass to the query

    Returns:
        List containing the query result in JSON format (changes are not persisted)
    """
    gel_client = gel.create_async_client()

    if globals:
        gel_client = gel_client.with_globals(**globals)

    result: str | None = None

    # Use a custom exception to force rollback while preserving the result
    class IntentionalRollback(Exception):
        pass

    try:
        async for tx in gel_client.transaction():
            async with tx:
                if arguments:
                    result = await tx.query_json(query, **arguments)
                else:
                    result = await tx.query_json(query)

                # Force a rollback by raising an exception after getting the result
                # This ensures the transaction is always rolled back
                raise IntentionalRollback("Intentional rollback for try_query")
    except IntentionalRollback:
        # This is expected - we intentionally caused a rollback
        pass

    if result is None:
        raise ValueError("Query returned None")

    parsed_result = json.loads(result)
    assert isinstance(parsed_result, list), (
        f"Expected list from query, got {type(parsed_result)}"
    )
    return parsed_result


def main() -> None:
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
        global WORKFLOWS_PATH
        WORKFLOWS_PATH = args.workflows_file

    if args.add_cursor_rules:
        static_dir = Path(__file__).parent / "static"
        cursor_rules_dir = Path.cwd() / ".cursor" / "rules"
        cursor_rules_dir.mkdir(parents=True, exist_ok=True)

        mdc_files = list(static_dir.glob("*.mdc"))

        if not mdc_files:
            raise FileNotFoundError(f"No .mdc files found in: {static_dir.as_posix()}")

        for source_file in mdc_files:
            dest_file = cursor_rules_dir / source_file.name
            shutil.copy2(source_file, dest_file)
    mcp.run()


if __name__ == "__main__":
    main()
