"""Tests for gel_mcp.import_from_workflows module."""

import json
import pytest
from pathlib import Path
from pydantic_core import ValidationError

from gel_mcp.import_from_workflows import import_from_workflows
from gel_mcp.common.types import MCPExample


def test_import_workflows_basic_functionality(workflows_file):
    """Test importing from existing workflows file with basic validation."""
    examples = import_from_workflows(workflows_file)

    assert len(examples) == 1
    assert isinstance(examples[0], MCPExample)
    assert examples[0].name == "Test Example"
    assert examples[0].slug == "test-example"


def test_import_multiple_workflows_and_empty_workflows(tmp_path):
    """Test importing from files with multiple workflows and empty workflows."""
    # Test multiple workflows
    multi_workflows_file = tmp_path / "multi_workflows.jsonl"

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

    with multi_workflows_file.open("w") as f:
        f.write(json.dumps(workflow1) + "\n")
        f.write(json.dumps(workflow2) + "\n")

    examples = import_from_workflows(multi_workflows_file)
    assert len(examples) == 2
    assert all(isinstance(ex, MCPExample) for ex in examples)
    assert examples[0].name == "First Example"
    assert examples[1].name == "Second Example"

    # Test empty workflows
    empty_workflows_file = tmp_path / "empty_workflows.jsonl"
    empty_workflow = {
        "id": "workflow-1",
        "name": "Empty Workflow",
        "tests": [],
        "examples": [],
    }

    with empty_workflows_file.open("w") as f:
        f.write(json.dumps(empty_workflow) + "\n")

    empty_examples = import_from_workflows(empty_workflows_file)
    assert len(empty_examples) == 0
    assert empty_examples == []


def test_import_error_cases(tmp_path):
    """Test error handling for nonexistent files and malformed JSON."""
    # Test nonexistent file
    nonexistent_file = tmp_path / "nonexistent.jsonl"
    with pytest.raises(FileNotFoundError, match="Workflows file not found"):
        import_from_workflows(nonexistent_file)

    # Test malformed JSON
    malformed_file = tmp_path / "malformed.jsonl"
    with malformed_file.open("w") as f:
        f.write('{"invalid": json content}\n')

    with pytest.raises(ValidationError):
        import_from_workflows(malformed_file)


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
