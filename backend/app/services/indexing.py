from sqlalchemy.orm import Session

from app.models.character import Character
from app.models.chapter import Chapter
from app.vector.store import get_vector_store


def _character_text(character: Character) -> str:
    parts = [
        character.name,
        character.description or "",
        character.current_status or "",
        " ".join(character.abilities_list),
        " ".join(character.tags_list),
    ]
    return "\n".join(p for p in parts if p)


def index_character(db: Session, character_id: str) -> None:
    character = db.get(Character, character_id)
    if not character:
        return
    get_vector_store().upsert(
        entity_type="character",
        entity_id=character.id,
        novel_id=character.novel_id,
        text=_character_text(character),
        metadata={"name": character.name},
    )


def index_chapter(db: Session, chapter_id: str) -> None:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        return
    text = "\n".join(p for p in [chapter.title, chapter.summary or "", chapter.content[:2000]] if p)
    get_vector_store().upsert(
        entity_type="chapter",
        entity_id=chapter.id,
        novel_id=chapter.novel_id,
        text=text,
        metadata={"title": chapter.title},
    )
