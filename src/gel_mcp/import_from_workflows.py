import os
from pathlib import Path
from gel_mcp.common.types import MCPExample, Workflow

"""
This is glue code to import examples from the Gel Workflow Creator.
"""


def import_from_workflows() -> list[MCPExample]:
    if not os.environ.get("GEL_MCP_WORKFLOWS_PATH"):
        raise ValueError("GEL_MCP_WORKFLOWS_PATH is not set")

    workflows_json_path = os.environ["GEL_MCP_WORKFLOWS_PATH"]
    if not Path(workflows_json_path).exists():
        raise FileNotFoundError(f"Workflows file not found: {workflows_json_path}")

    with Path(workflows_json_path).open("r") as f:
        workflows = [Workflow.model_validate_json(line) for line in f]

    mcp_examples = []
    for workflow in workflows:
        for example in workflow.examples:
            mcp_examples.append(MCPExample.from_workflow_example(example))

    return mcp_examples
