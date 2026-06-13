from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class ChapterCreate(BaseModel):
    novel_id: str
    title: str = Field(min_length=1, max_length=255)
    summary: str | None = None
    status: str = "draft"


class ChapterUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    summary: str | None = None
    content: str | None = None
    status: str | None = None


class ChapterOut(ORMBase):
    id: str
    novel_id: str
    title: str
    summary: str | None
    content: str
    word_count: int
    status: str
    created_at: datetime
    updated_at: datetime
