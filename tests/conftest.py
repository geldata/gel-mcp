"""Test configuration and fixtures for gel-mcp tests."""

import json
import subprocess
import pytest

from gel_mcp.common.types import MCPExample, CodeSnippet


@pytest.fixture
def code_snippet():
    """Simple code snippet for testing."""
    return CodeSnippet(
        id="test-snippet-1",
        url="test://example.gel",
        code="type User { name: str; }",
        language="gel",
    )


@pytest.fixture
def mcp_example(code_snippet):
    """Simple MCP example for testing."""
    return MCPExample(
        id="test-example-1",
        slug="test-example",
        name="Test Example",
        description="A test example for unit testing",
        instructions="This is a test example",
        code=[code_snippet],
    )


@pytest.fixture
def sample_examples():
    """Multiple test examples for server testing."""
    return [
        MCPExample(
            id="test-1",
            slug="test-example-1",
            name="Test Example 1",
            description="First test example",
            instructions="Test instructions 1",
            code=[],
        ),
        MCPExample(
            id="test-2",
            slug="test-example-2",
            name="Test Example 2",
            description="Second test example",
            instructions="Test instructions 2",
            code=[],
        ),
    ]


@pytest.fixture
def workflows_file(tmp_path, mcp_example):
    """Temporary workflows.jsonl file for testing."""
    workflows_file = tmp_path / "test_workflows.jsonl"

    workflow_data = {
        "id": "test-workflow-1",
        "name": "Test Workflow",
        "tests": [],
        "examples": [
            {
                "id": mcp_example.id,
                "name": mcp_example.name,
                "slug": mcp_example.slug,
                "description": mcp_example.description,
                "instructions": mcp_example.instructions,
                "code": [snippet.model_dump() for snippet in mcp_example.code],
            }
        ],
    }

    with workflows_file.open("w") as f:
        f.write(json.dumps(workflow_data) + "\n")

    return workflows_file


@pytest.fixture(scope="session")
async def gel_is_initialized():
    import gel

    def run_in_shell(command: list[str]):
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=False, timeout=60
            )
        except FileNotFoundError:
            pytest.skip("The 'gel' command was not found in your PATH.")
        except subprocess.TimeoutExpired:
            pytest.skip(f"Command '{' '.join(command)}' timed out.")

        if result.returncode != 0:
            error_message = f"Error: {result.stderr}"
            pytest.skip(error_message)

    try:
        client = gel.create_async_client()
        await client.ensure_connected()
        await client.query("reset schema to initial ;")
        run_in_shell(["gel", "migrate"])
        await client.aclose()
        yield
        return
    except gel.errors.ClientConnectionError:
        print("Gel connection failed. Attempting to initialize project...")

    run_in_shell(["gel", "project", "init", "--non-interactive"])
    yield
