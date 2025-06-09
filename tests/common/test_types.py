"""Tests for gel_mcp.common.types custom business logic."""

from gel_mcp.common.types import CodeSnippet, Example, MCPExample


def test_slug_generation_from_name():
    """Test slug generation from example name."""
    workflow_example = Example(id="test-1", name="Create User Authentication System")

    mcp_example = MCPExample.from_workflow_example(workflow_example)

    assert mcp_example.slug == "create-user-authentication-system"


def test_slug_generation_truncates_long_names():
    """Test slug generation truncates to first 5 words."""
    workflow_example = Example(
        id="test-1", name="This Is A Very Long Example Name That Should Be Truncated"
    )

    mcp_example = MCPExample.from_workflow_example(workflow_example)

    assert mcp_example.slug == "this-is-a-very-long"


def test_slug_fallback_when_no_name():
    """Test fallback slug when example has no name."""
    workflow_example = Example(id="test-1")

    mcp_example = MCPExample.from_workflow_example(workflow_example)

    assert mcp_example.slug == "fake-slug"


def test_markdown_generation_complete():
    """Test markdown generation includes all components."""
    code_snippet = CodeSnippet(
        id="test-1", url="schema.gel", code="type User { name: str; }", language="gel"
    )

    example = MCPExample(
        id="test-1",
        slug="test-example",
        name="Test Example",
        description="Test description",
        instructions="Follow these steps",
        code=[code_snippet],
    )

    markdown = example.to_markdown()

    assert "Example: Test Example (test-example)" in markdown
    assert "Test description" in markdown
    assert "Follow these steps" in markdown
    assert "From schema.gel" in markdown
    assert "```gel" in markdown
    assert "type User { name: str; }" in markdown


def test_markdown_generation_without_url():
    """Test markdown generation when code snippet has no URL."""
    code_snippet = CodeSnippet(id="test-1", code="select User;", language="edgeql")

    example = MCPExample(
        id="test-1",
        slug="test",
        name="Test",
        description="Test description",
        instructions="Test instructions",
        code=[code_snippet],
    )

    markdown = example.to_markdown()

    assert "From" not in markdown
    assert "```edgeql" in markdown
    assert "select User;" in markdown
