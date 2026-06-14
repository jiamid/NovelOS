from pydantic import BaseModel, Field


class WritingRulesOut(BaseModel):
    content: str
    file_path: str


class WritingRulesUpdate(BaseModel):
    content: str = Field(min_length=1)
