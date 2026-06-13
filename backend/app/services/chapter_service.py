from sqlalchemy.orm import Session

from app.models.chapter import Chapter
from app.services.indexing_tasks import enqueue_index_chapter
from app.utils.text import count_words


def chapter_to_dict(chapter: Chapter, *, include_content: bool = False) -> dict:
    data = {
        "id": chapter.id,
        "novel_id": chapter.novel_id,
        "title": chapter.title,
        "summary": chapter.summary,
        "word_count": chapter.word_count,
        "status": chapter.status,
        "updated_at": chapter.updated_at.isoformat(),
    }
    if include_content:
        data["content"] = chapter.content
    return data


def save_chapter_content(db: Session, chapter_id: str, content: str) -> Chapter:
    chapter = db.get(Chapter, chapter_id)
    if not chapter:
        raise ValueError(f"Chapter {chapter_id} not found")
    chapter.content = content
    chapter.word_count = count_words(content)
    db.commit()
    db.refresh(chapter)
    enqueue_index_chapter(chapter.id)
    return chapter
