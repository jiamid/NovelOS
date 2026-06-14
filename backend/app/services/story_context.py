from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.models.character import Character, CharacterRelation
from app.models.chapter import Chapter
from app.models.event import Event, Timeline
from app.models.novel import Novel
from app.services.chapter_service import chapter_to_dict
from app.services.event_service import event_to_timeline_dict
from app.services.writing_rules import get_writing_rules
from app.utils.serialization import character_to_dict
from app.vector.store import get_vector_store


def get_story_context(db: Session, novel_id: str, chapter_id: str | None = None) -> dict:
    settings = get_settings()
    novel = db.get(Novel, novel_id)
    if not novel:
        raise ValueError(f"Novel {novel_id} not found")

    chapters = db.execute(
        select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.updated_at.desc())
    ).scalars().all()

    current: Chapter | None = None
    if chapter_id:
        current = db.get(Chapter, chapter_id)
        if not current or current.novel_id != novel_id:
            raise ValueError(f"Chapter {chapter_id} not found in novel {novel_id}")
    elif chapters:
        current = chapters[0]

    characters = db.execute(
        select(Character).where(Character.novel_id == novel_id)
    ).scalars().all()
    char_ids = [c.id for c in characters]
    relations = []
    if char_ids:
        relations = db.execute(
            select(CharacterRelation).where(CharacterRelation.source_id.in_(char_ids))
        ).scalars().all()
    name_map = {c.id: c.name for c in characters}

    timelines = (
        db.execute(
            select(Timeline)
            .options(joinedload(Timeline.event).joinedload(Event.characters))
            .where(Timeline.novel_id == novel_id)
            .order_by(Timeline.sequence)
        )
        .unique()
        .scalars()
        .all()
    )

    query_parts = [novel.name, novel.description or ""]
    if current:
        query_parts.extend([current.title, current.summary or "", (current.content or "")[:500]])
    search_query = "\n".join(p for p in query_parts if p)
    vector_hits = get_vector_store().search(
        query=search_query,
        novel_id=novel_id,
        top_k=settings.vector_top_k,
    )

    return {
        "writing_rules": get_writing_rules(),
        "novel": {
            "id": novel.id,
            "name": novel.name,
            "description": novel.description,
        },
        "current_chapter": chapter_to_dict(current, include_content=True) if current else None,
        "chapters": [chapter_to_dict(c) for c in chapters],
        "characters": [character_to_dict(c) for c in characters],
        "character_relations": [
            {
                "source_id": r.source_id,
                "source_name": name_map.get(r.source_id),
                "target_id": r.target_id,
                "target_name": name_map.get(r.target_id),
                "relation_type": r.relation_type,
            }
            for r in relations
        ],
        "timeline": [
            {
                "id": t.id,
                "sequence": t.sequence,
                "event": event_to_timeline_dict(t.event) if t.event else None,
            }
            for t in timelines
        ],
        "vector_hits": vector_hits,
    }
