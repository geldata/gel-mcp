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

    with patch("gel_mcp.server.fetch_examples", return_value=sample_examples):
        result = await list_examples()
        assert len(result) == 2
        assert result[0] == "<test-example-1> Test Example 1: First test example"
        assert result[1] == "<test-example-2> Test Example 2: Second test example"

        example_result = await fetch_example("test-example-1")
        assert example_result is not None
        assert "Test Example 1" in example_result
        assert "First test example" in example_result

        missing_result = await fetch_example("nonexistent")
        assert missing_result is None


@pytest.mark.asyncio
async def test_execute_query(gel_is_initialized):
    from gel_mcp.server import execute_query

    result = await execute_query("select 42")
    assert result == [42]


@pytest.mark.asyncio
async def test_try_query_rolls_back(gel_is_initialized):
    from gel_mcp.server import try_query, execute_query

    await try_query("insert Kek { pek := 'test' }")
    result = await execute_query("select Kek { pek }")
    assert result == []


@pytest.mark.asyncio
async def test_execute_query_with_arguments(gel_is_initialized):
    from gel_mcp.server import execute_query

    await execute_query("insert Kek { pek := <str>$pek }", {"pek": "test"})
    result = await execute_query("select Kek { pek }")
    assert result == [{"pek": "test"}]
    await execute_query("delete Kek")
