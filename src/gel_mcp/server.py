from mcp.server.fastmcp import FastMCP
from pathlib import Path
import gel
import argparse
import json
from typing import Any

from gel_mcp.import_from_workflows import import_from_workflows
from gel_mcp.common.types import MCPExample


mcp = FastMCP("gel-mcp")

WORKFLOWS_PATH = Path(__file__).parent / "static" / "workflows.jsonl"
assert WORKFLOWS_PATH.exists(), "Workflows file does not exist"
assert WORKFLOWS_PATH.is_file(), "Workflows file is not a file"

RULES_DIR = Path(__file__).parent / "static" / "gel-ai-rules" / "src"
assert RULES_DIR.exists(), "Rules directory does not exist"
assert RULES_DIR.is_dir(), "Rules directory is not a directory"


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


@mcp.tool()
async def list_rules() -> list[str]:
    """
    List all available rules
    Rules are Markdown files that contain examples and instructions for AI agents on how to use Gel.
    They are crucial for correct code generation.
    """
    return [rule.name for rule in RULES_DIR.glob("*.md")]


@mcp.tool()
async def fetch_rule(rule_name: str) -> str:
    """
    Fetch a rule by its name
    E.g. gel.md or gel-python.md
    """
    rule_path = RULES_DIR / rule_name
    if not rule_path.exists():
        raise FileNotFoundError(f"Rule {rule_name} not found")
    return rule_path.read_text()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workflows-file", type=Path, required=False, help="Path to workflows.jsonl"
    )

    args = parser.parse_args()

    if args.workflows_file:
        global WORKFLOWS_PATH
        WORKFLOWS_PATH = args.workflows_file

    mcp.run()


if __name__ == "__main__":
    main()
