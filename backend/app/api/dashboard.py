from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.character import Character
from app.models.event import Event
from app.models.chapter import Chapter
from app.models.novel import Novel

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return {
        "novel_count": db.scalar(select(func.count()).select_from(Novel)) or 0,
        "chapter_count": db.scalar(select(func.count()).select_from(Chapter)) or 0,
        "character_count": db.scalar(select(func.count()).select_from(Character)) or 0,
        "event_count": db.scalar(select(func.count()).select_from(Event)) or 0,
    }
