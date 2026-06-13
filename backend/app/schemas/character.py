from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class CharacterCreate(BaseModel):
    novel_id: str
    name: str = Field(min_length=1, max_length=255)
    gender: str | None = None
    birthday: str | None = None
    description: str | None = None
    current_status: str | None = None
    abilities: list[str] = []
    tags: list[str] = []


class CharacterUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    gender: str | None = None
    birthday: str | None = None
    description: str | None = None
    current_status: str | None = None
    abilities: list[str] | None = None
    tags: list[str] | None = None


class CharacterOut(ORMBase):
    id: str
    novel_id: str
    name: str
    gender: str | None
    birthday: str | None
    description: str | None
    current_status: str | None
    abilities: list[str]
    tags: list[str]
    created_at: datetime
    updated_at: datetime


class CharacterRelationCreate(BaseModel):
    source_id: str
    target_id: str
    relation_type: str


class CharacterRelationOut(ORMBase):
    source_id: str
    target_id: str
    relation_type: str
