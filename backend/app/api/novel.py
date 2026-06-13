from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.database import get_db
from app.models.novel import Novel
from app.schemas.common import PaginatedResponse
from app.schemas.novel import NovelCreate, NovelOut, NovelUpdate
from app.services.novel_service import delete_novel as delete_novel_service

router = APIRouter(prefix="/novel", tags=["novel"])


@router.get("", response_model=PaginatedResponse[NovelOut])
def list_novels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    total = db.scalar(select(func.count()).select_from(Novel)) or 0
    items = (
        db.execute(select(Novel).offset((page - 1) * page_size).limit(page_size))
        .scalars()
        .all()
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=NovelOut, status_code=201)
def create_novel(payload: NovelCreate, db: Session = Depends(get_db)):
    item = Novel(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{novel_id}", response_model=NovelOut)
def get_novel(novel_id: str, db: Session = Depends(get_db)):
    return get_or_404(db, Novel, novel_id)


@router.put("/{novel_id}", response_model=NovelOut)
def update_novel(novel_id: str, payload: NovelUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, Novel, novel_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{novel_id}", status_code=204)
def delete_novel(novel_id: str, db: Session = Depends(get_db)):
    get_or_404(db, Novel, novel_id)
    try:
        delete_novel_service(db, novel_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
