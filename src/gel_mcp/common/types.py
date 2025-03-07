from pydantic import BaseModel


class CodeExample(BaseModel):
    slug: str 
    description: str
    language: str
    code: str
    notes: str | None = None


class WorkflowExample(BaseModel):
    slug: str
    description: str
    instructions: str
