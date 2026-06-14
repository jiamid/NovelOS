import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.character import Character, CharacterRelation
from app.models.chapter import Chapter
from app.models.event import Event, Timeline
from app.models.novel import Novel
from app.mcp.logging import log_mcp_call
from app.services.character_service import search_character
from app.services.chapter_service import chapter_to_dict, save_chapter_content
from app.services.event_service import event_to_timeline_dict
from app.services.story_context import get_story_context
from app.services.writing_rules import get_writing_rules
from app.utils.serialization import character_to_dict


def _summary(data: Any, max_len: int = 200) -> str:
    text = json.dumps(data, ensure_ascii=False)
    return text[:max_len] + ("..." if len(text) > max_len else "")


def handle_get_story_context(db: Session, arguments: dict) -> dict:
    result = get_story_context(
        db,
        novel_id=arguments["novel_id"],
        chapter_id=arguments.get("chapter_id"),
    )
    log_mcp_call(db, "get_story_context", arguments, True, _summary(result))
    return result


def handle_get_writing_rules(db: Session, arguments: dict) -> dict:
    result = {"writing_rules": get_writing_rules()}
    log_mcp_call(db, "get_writing_rules", arguments, True, _summary(result))
    return result


def handle_get_novel(db: Session, arguments: dict) -> dict:
    novel = db.get(Novel, arguments["novel_id"])
    if not novel:
        raise ValueError(f"Novel {arguments['novel_id']} not found")
    result = {
        "id": novel.id,
        "name": novel.name,
        "description": novel.description,
    }
    log_mcp_call(db, "get_novel", arguments, True, _summary(result))
    return result


def handle_list_chapters(db: Session, arguments: dict) -> dict:
    novel_id = arguments["novel_id"]
    chapters = db.execute(
        select(Chapter).where(Chapter.novel_id == novel_id).order_by(Chapter.updated_at.desc())
    ).scalars().all()
    result = {"chapters": [chapter_to_dict(c) for c in chapters]}
    log_mcp_call(db, "list_chapters", arguments, True, _summary(result))
    return result


def handle_get_chapter(db: Session, arguments: dict) -> dict:
    chapter_id = arguments["chapter_id"]
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise ValueError(f"Chapter {chapter_id} not found")
    result = chapter_to_dict(chapter, include_content=True)
    log_mcp_call(db, "get_chapter", arguments, True, _summary(result))
    return result


def handle_save_chapter_content(db: Session, arguments: dict) -> dict:
    chapter = save_chapter_content(db, arguments["chapter_id"], arguments["content"])
    result = {
        "chapter_id": chapter.id,
        "word_count": chapter.word_count,
        "title": chapter.title,
    }
    log_mcp_call(db, "save_chapter_content", arguments, True, _summary(result))
    return result


def handle_update_chapter(db: Session, arguments: dict) -> dict:
    chapter_id = arguments["chapter_id"]
    data = arguments.get("data", {})
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise ValueError(f"Chapter {chapter_id} not found")
    allowed = {"title", "summary", "status", "content"}
    for key, value in data.items():
        if key in allowed:
            setattr(chapter, key, value)
    if "content" in data:
        from app.utils.text import count_words

        chapter.word_count = count_words(chapter.content or "")
    db.commit()
    db.refresh(chapter)
    if "content" in data:
        from app.services.indexing_tasks import enqueue_index_chapter

        enqueue_index_chapter(chapter.id)
    result = chapter_to_dict(chapter, include_content=True)
    log_mcp_call(db, "update_chapter", arguments, True, _summary(result))
    return result


def handle_search_character(db: Session, arguments: dict) -> dict:
    results = search_character(
        db,
        keyword=arguments["keyword"],
        novel_id=arguments.get("novel_id"),
    )
    result = {"characters": results}
    log_mcp_call(db, "search_character", arguments, True, _summary(result))
    return result


def handle_list_characters(db: Session, arguments: dict) -> dict:
    novel_id = arguments["novel_id"]
    characters = db.execute(
        select(Character).where(Character.novel_id == novel_id)
    ).scalars().all()
    result = {"characters": [character_to_dict(c) for c in characters]}
    log_mcp_call(db, "list_characters", arguments, True, _summary(result))
    return result


def handle_get_character_relations(db: Session, arguments: dict) -> dict:
    novel_id = arguments["novel_id"]
    characters = db.execute(
        select(Character).where(Character.novel_id == novel_id)
    ).scalars().all()
    char_ids = [c.id for c in characters]
    name_map = {c.id: c.name for c in characters}
    if not char_ids:
        result = {"relations": []}
    else:
        relations = db.execute(
            select(CharacterRelation).where(CharacterRelation.source_id.in_(char_ids))
        ).scalars().all()
        result = {
            "relations": [
                {
                    "source_id": r.source_id,
                    "source_name": name_map.get(r.source_id),
                    "target_id": r.target_id,
                    "target_name": name_map.get(r.target_id),
                    "relation_type": r.relation_type,
                }
                for r in relations
            ]
        }
    log_mcp_call(db, "get_character_relations", arguments, True, _summary(result))
    return result


def handle_get_timeline(db: Session, arguments: dict) -> dict:
    novel_id = arguments["novel_id"]
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
    result = {
        "timeline": [
            {
                "id": t.id,
                "sequence": t.sequence,
                "event": event_to_timeline_dict(t.event) if t.event else None,
            }
            for t in timelines
        ]
    }
    log_mcp_call(db, "get_timeline", arguments, True, _summary(result))
    return result
