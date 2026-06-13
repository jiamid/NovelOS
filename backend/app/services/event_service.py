from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.character import Character
from app.models.event import Event
from app.schemas.event import EventCharacterBrief, EventOut


def sync_event_characters(db: Session, event: Event, character_ids: list[str] | None) -> None:
    if character_ids is None:
        return
    if not character_ids:
        event.characters = []
        return
    chars = db.execute(select(Character).where(Character.id.in_(character_ids))).scalars().all()
    event.characters = list(chars)


def event_to_out(event: Event) -> EventOut:
    return EventOut(
        id=event.id,
        novel_id=event.novel_id,
        title=event.title,
        description=event.description,
        occur_time=event.occur_time,
        location=event.location,
        characters=[EventCharacterBrief(id=c.id, name=c.name) for c in event.characters],
        character_ids=[c.id for c in event.characters],
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


def event_to_timeline_dict(event: Event) -> dict:
    return {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "occur_time": event.occur_time,
        "location": event.location,
        "characters": [{"id": c.id, "name": c.name} for c in event.characters],
    }
