from pydantic import BaseModel, Field


"""
Note: The types below are copied over from the Workflow Creator (url).
They are duplicated here to validate JSON blobs that we are using instead of
a proper database.
"""


class CodeSnippet(BaseModel):
    """A piece of code. Can be an entire file or a snippet from a file."""

    id: str
    url: str | None = None
    code: str | None = None
    language: str | None = None


class Example(BaseModel):
    """An example served to the agent via the MCP server to help it complete the workflow."""

    id: str
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    instructions: str | None = None
    code: list[CodeSnippet] = Field(default_factory=list)


class Test(BaseModel):
    """A test case to manually run against the agent"""

    id: str
    test_prompt: str | None = None
    expected_outcome: str | None = None
    initial_state: list[CodeSnippet] = Field(default_factory=list)


class Workflow(BaseModel):
    """A workflow that describes implementing an app feature using Gel"""

    id: str
    name: str | None = None
    tests: list[Test] = Field(default_factory=list)
    examples: list[Example] = Field(default_factory=list)


"""
Note: The following code is native to the MCP server.
"""

MARKDOWN_EXAMPLE_TEMPLATE = """
Example: {name} ({slug})

{description}

{body}
""".strip()

MARKDOWN_CODE_SNIPPET_TEMPLATE = """
```{language}
{code}
```
""".strip()


class MCPExample(Example):
    slug: str | None = None

    @classmethod
    def from_workflow_example(cls, example: Example) -> "MCPExample":
        def name_to_slug(name: str) -> str:
            short_name = name.lower().split(" ")[:5]
            return "-".join(short_name)

        slug = name_to_slug(example.name)

        return cls(
            id=example.id,
            slug=slug or "fake-slug",
            name=example.name,
            description=example.description,
            instructions=example.instructions,
            code=example.code,
        )

    def to_markdown(self) -> str:
        formatted_code = []
        for code_snippet in self.code:
            formatted_code.append(
                f"From {code_snippet.url}\n"
                if code_snippet.url
                else ""
                + MARKDOWN_CODE_SNIPPET_TEMPLATE.format(
                    language=code_snippet.language,
                    code=code_snippet.code,
                )
            )

        body = self.instructions if self.instructions else ""
        body += "\n".join(formatted_code)

        return MARKDOWN_EXAMPLE_TEMPLATE.format(
            name=self.name,
            slug=self.slug,
            description=self.description,
            body=body,
        )
