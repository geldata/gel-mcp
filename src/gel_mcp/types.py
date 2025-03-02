from pydantic import BaseModel


class CodeExample(BaseModel):
    description: str
    language: str
    text: str