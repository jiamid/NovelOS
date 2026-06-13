from fastapi import APIRouter, BackgroundTasks, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.database import get_db
from app.models.chapter import Chapter
from app.schemas.chapter import ChapterCreate, ChapterOut, ChapterUpdate
from app.schemas.common import PaginatedResponse
from app.services.indexing_tasks import schedule_index_chapter
from app.utils.text import count_words

router = APIRouter(prefix="/chapter", tags=["chapter"])


@router.get("", response_model=PaginatedResponse[ChapterOut])
def list_chapters(
    novel_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Chapter)
    if novel_id:
        query = query.where(Chapter.novel_id == novel_id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=ChapterOut, status_code=201)
def create_chapter(payload: ChapterCreate, db: Session = Depends(get_db)):
    item = Chapter(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{chapter_id}", response_model=ChapterOut)
def get_chapter(chapter_id: str, db: Session = Depends(get_db)):
    return get_or_404(db, Chapter, chapter_id)


@router.put("/{chapter_id}", response_model=ChapterOut)
def update_chapter(
    chapter_id: str,
    payload: ChapterUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    item = get_or_404(db, Chapter, chapter_id)
    data = payload.model_dump(exclude_unset=True)
    if "content" in data:
        data["word_count"] = count_words(data["content"] or "")
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    if "content" in data:
        background_tasks.add_task(schedule_index_chapter, item.id)
    return item


@router.delete("/{chapter_id}", status_code=204)
def delete_chapter(chapter_id: str, db: Session = Depends(get_db)):
    item = get_or_404(db, Chapter, chapter_id)
    db.delete(item)
    db.commit()
