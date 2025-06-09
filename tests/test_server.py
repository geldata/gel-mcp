"""Tests for gel_mcp.server module."""

import json
import pytest
from unittest.mock import patch


def test_server_entrypoint_exists():
    """Test that the server main function exists and is callable."""
    from gel_mcp.server import main

    assert callable(main)


@pytest.mark.asyncio
async def test_list_examples_format(sample_examples):
    """Test list_examples returns correctly formatted strings."""
    from gel_mcp.server import list_examples

    with patch("gel_mcp.server._get_mcp_examples", return_value=sample_examples):
        result = await list_examples()

        assert len(result) == 2
        assert result[0] == "<test-example-1> Test Example 1: First test example"
        assert result[1] == "<test-example-2> Test Example 2: Second test example"


@pytest.mark.asyncio
async def test_fetch_example_existing(sample_examples):
    """Test fetch_example returns markdown for valid slug."""
    from gel_mcp.server import fetch_example

    with patch("gel_mcp.server._get_mcp_examples", return_value=sample_examples):
        result = await fetch_example("test-example-1")

        assert result is not None
        assert "Test Example 1" in result
        assert "First test example" in result


@pytest.mark.asyncio
async def test_fetch_example_missing(sample_examples):
    """Test fetch_example returns None for invalid slug."""
    from gel_mcp.server import fetch_example

    with patch("gel_mcp.server._get_mcp_examples", return_value=sample_examples):
        result = await fetch_example("nonexistent")

        assert result is None


@pytest.mark.asyncio
async def test_execute_query_json_parsing(mock_gel_client):
    """Test execute_query correctly parses JSON response."""
    from gel_mcp.server import execute_query

    test_data = {"users": [{"name": "Alice"}]}
    mock_gel_client.query_json.return_value = json.dumps(test_data)

    result = await execute_query("select User { name }")

    assert result == test_data
    mock_gel_client.query_json.assert_called_once_with("select User { name }")


@pytest.mark.asyncio
async def test_execute_query_with_arguments(mock_gel_client):
    """Test execute_query passes arguments correctly."""
    from gel_mcp.server import execute_query

    test_data = {"user": {"name": "Bob"}}
    mock_gel_client.query_json.return_value = json.dumps(test_data)

    result = await execute_query(
        "select User filter .id = $user_id", {"user_id": "123"}
    )

    assert result == test_data
    mock_gel_client.query_json.assert_called_once_with(
        "select User filter .id = $user_id", user_id="123"
    )


@pytest.mark.asyncio
async def test_execute_query_invalid_json_raises_error(mock_gel_client):
    """Test execute_query raises JSONDecodeError for invalid JSON response."""
    from gel_mcp.server import execute_query

    mock_gel_client.query_json.return_value = "invalid json"

    with pytest.raises(json.JSONDecodeError):
        await execute_query("select User { name }")


@pytest.mark.asyncio
async def test_try_query_returns_result(mock_gel_client):
    """Test try_query executes in transaction."""
    from gel_mcp.server import try_query

    result = await try_query("insert User { name := 'Test' }")

    assert result == {"result": "test_data"}
