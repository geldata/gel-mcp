"""Tests for gel_mcp.server module."""

import pytest
from unittest.mock import patch


def test_server_entrypoint_exists():
    """Test that the server main function exists and is callable."""
    from gel_mcp.server import main

    assert callable(main)


@pytest.mark.asyncio
async def test_examples_functionality(sample_examples):
    """Test list_examples and fetch_example work correctly with sample data."""
    from gel_mcp.server import list_examples, fetch_example

    with patch("gel_mcp.server._get_mcp_examples", return_value=sample_examples):
        # Test list_examples format
        result = await list_examples()
        assert len(result) == 2
        assert result[0] == "<test-example-1> Test Example 1: First test example"
        assert result[1] == "<test-example-2> Test Example 2: Second test example"

        # Test fetch_example with existing slug
        example_result = await fetch_example("test-example-1")
        assert example_result is not None
        assert "Test Example 1" in example_result
        assert "First test example" in example_result

        # Test fetch_example with non-existent slug
        missing_result = await fetch_example("nonexistent")
        assert missing_result is None
