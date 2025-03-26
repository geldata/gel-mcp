from pathlib import Path
from gel_mcp.common.types import MCPExample, Workflow

"""
This is glue code to import examples from the Gel Workflow Creator.
"""


def import_from_workflows(workflows_file: Path) -> list[MCPExample]:
    if not workflows_file.exists():
        raise FileNotFoundError(f"Workflows file not found: {workflows_file}")

    with workflows_file.open("r") as f:
        workflows = [Workflow.model_validate_json(line) for line in f]

    mcp_examples = []
    for workflow in workflows:
        for example in workflow.examples:
            mcp_examples.append(MCPExample.from_workflow_example(example))

    return mcp_examples
