"""Tests for gel_mcp.import_from_workflows module."""

import json
import pytest
from pathlib import Path
from pydantic_core import ValidationError

from gel_mcp.import_from_workflows import import_from_workflows
from gel_mcp.common.types import MCPExample


def test_import_from_existing_workflows_file(workflows_file):
    """Test importing from an existing workflows file."""
    examples = import_from_workflows(workflows_file)

    assert len(examples) == 1
    assert isinstance(examples[0], MCPExample)
    assert examples[0].name == "Test Example"
    assert examples[0].slug == "test-example"


def test_import_from_nonexistent_file(tmp_path):
    """Test importing from a nonexistent file raises FileNotFoundError."""
    nonexistent_file = tmp_path / "nonexistent.jsonl"

    with pytest.raises(FileNotFoundError, match="Workflows file not found"):
        import_from_workflows(nonexistent_file)


def test_import_multiple_workflows(tmp_path):
    """Test importing from a file with multiple workflows."""
    workflows_file = tmp_path / "multi_workflows.jsonl"

    workflow1 = {
        "id": "workflow-1",
        "name": "First Workflow",
        "tests": [],
        "examples": [
            {
                "id": "example-1",
                "name": "First Example",
                "description": "First test example",
                "instructions": "First instructions",
                "code": [],
            }
        ],
    }

    workflow2 = {
        "id": "workflow-2",
        "name": "Second Workflow",
        "tests": [],
        "examples": [
            {
                "id": "example-2",
                "name": "Second Example",
                "description": "Second test example",
                "instructions": "Second instructions",
                "code": [],
            }
        ],
    }

    with workflows_file.open("w") as f:
        f.write(json.dumps(workflow1) + "\n")
        f.write(json.dumps(workflow2) + "\n")

    examples = import_from_workflows(workflows_file)

    assert len(examples) == 2
    assert all(isinstance(ex, MCPExample) for ex in examples)
    assert examples[0].name == "First Example"
    assert examples[1].name == "Second Example"


def test_import_workflow_with_no_examples(tmp_path):
    """Test importing from a workflow with no examples."""
    workflows_file = tmp_path / "no_examples.jsonl"

    workflow = {
        "id": "workflow-1",
        "name": "Empty Workflow",
        "tests": [],
        "examples": [],
    }

    with workflows_file.open("w") as f:
        f.write(json.dumps(workflow) + "\n")

    examples = import_from_workflows(workflows_file)

    assert len(examples) == 0
    assert examples == []


def test_import_malformed_json(tmp_path):
    """Test importing from a file with malformed JSON."""
    workflows_file = tmp_path / "malformed.jsonl"

    with workflows_file.open("w") as f:
        f.write('{"invalid": json content}\n')

    with pytest.raises(ValidationError):
        import_from_workflows(workflows_file)


def test_default_workflows_file_exists():
    """Test that the default workflows file exists in the expected location."""
    workflows_path = (
        Path(__file__).parent.parent / "src" / "gel_mcp" / "static" / "workflows.jsonl"
    )

    if workflows_path.exists():
        # If it exists, it should be valid JSON
        examples = import_from_workflows(workflows_path)
        assert isinstance(examples, list)
    else:
        pytest.skip(
            "Default workflows.jsonl file not found - server will need workflows file argument"
        )
