from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class NovelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None


class NovelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class NovelOut(ORMBase):
    id: str
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
