from mcp.server import FastMCP
from pathlib import Path

from gel_mcp.common.types import CodeExample


mcp = FastMCP("gel-mcp")


with (Path(__file__).parent / ("code_examples.jsonl")).open("r") as f:
    code_examples = [CodeExample.model_validate_json(line) for line in f]


@mcp.resource("code://list-examples")
async def list_code_examples() -> list[str]:
    return [f"{e.slug}: {e.description}" for e in code_examples]


@mcp.resource("code://get-example/{slug}")
async def get_code_example(slug: str) -> str | None:
    return next((e for e in code_examples if e.slug == slug), None)

def main():
    mcp.run()

if __name__ == "__main__":
    main()