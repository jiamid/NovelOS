import logging
import threading

from app.database import SessionLocal
from app.services.indexing import index_character, index_chapter

logger = logging.getLogger(__name__)


def schedule_index_character(character_id: str) -> None:
    db = SessionLocal()
    try:
        index_character(db, character_id)
    except Exception:
        logger.exception("Failed to index character %s", character_id)
    finally:
        db.close()


def schedule_index_chapter(chapter_id: str) -> None:
    db = SessionLocal()
    try:
        index_chapter(db, chapter_id)
    except Exception:
        logger.exception("Failed to index chapter %s", chapter_id)
    finally:
        db.close()


def enqueue_index_character(character_id: str) -> None:
    threading.Thread(target=schedule_index_character, args=(character_id,), daemon=True).start()


def enqueue_index_chapter(chapter_id: str) -> None:
    threading.Thread(target=schedule_index_chapter, args=(chapter_id,), daemon=True).start()
