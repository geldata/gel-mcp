from pydantic import BaseModel, Field


class GelState(BaseModel):
    description: str | None = None
    dbschema: str | None = None
    data: str | None = None
    queries: str | None = None


class TestCase(BaseModel):
    test_id: str
    prompt: str | None = None
    initial_state: GelState | None = None
    expected_steps: list[str] = []
    expected_outcome: GelState | None = None


class Workflow(BaseModel):
    workflow_id: str
    workflow_name: str | None = None
    description: str | None = None
    test_cases: list[TestCase] = Field(default_factory=list)
