from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class EventCharacterBrief(BaseModel):
    id: str
    name: str


class EventCreate(BaseModel):
    novel_id: str
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    occur_time: str | None = None
    location: str | None = None
    character_ids: list[str] = []


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    occur_time: str | None = None
    location: str | None = None
    character_ids: list[str] | None = None


class EventOut(ORMBase):
    id: str
    novel_id: str
    title: str
    description: str | None
    occur_time: str | None
    location: str | None
    characters: list[EventCharacterBrief] = []
    character_ids: list[str] = []
    created_at: datetime
    updated_at: datetime


class TimelineCreate(BaseModel):
    novel_id: str
    event_id: str
    sequence: int = 0


class TimelineUpdate(BaseModel):
    sequence: int | None = None


class TimelineOut(ORMBase):
    id: str
    novel_id: str
    event_id: str
    sequence: int
    created_at: datetime
    updated_at: datetime


class TimelineEventOut(BaseModel):
    id: str
    title: str
    description: str | None
    occur_time: str | None
    location: str | None = None
    characters: list[EventCharacterBrief] = []


class TimelineWithEventOut(BaseModel):
    id: str
    novel_id: str
    event_id: str
    sequence: int
    event: TimelineEventOut | None = None
