from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_or_404
from app.database import get_db
from app.models.event import Event, Timeline
from app.schemas.common import PaginatedResponse
from app.schemas.event import TimelineCreate, TimelineOut, TimelineUpdate, TimelineWithEventOut
from app.services.event_service import event_to_timeline_dict

router = APIRouter(prefix="/timeline", tags=["timeline"])

_EVENT_LOAD = (joinedload(Timeline.event).joinedload(Event.characters),)


@router.get("", response_model=PaginatedResponse[TimelineOut])
def list_timelines(
    novel_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Timeline)
    if novel_id:
        query = query.where(Timeline.novel_id == novel_id)
    query = query.order_by(Timeline.sequence)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/with-events", response_model=list[TimelineWithEventOut])
def list_timelines_with_events(novel_id: str, db: Session = Depends(get_db)):
    timelines = (
        db.execute(
            select(Timeline)
            .options(*_EVENT_LOAD)
            .where(Timeline.novel_id == novel_id)
            .order_by(Timeline.sequence)
        )
        .unique()
        .scalars()
        .all()
    )
    return [
        TimelineWithEventOut(
            id=t.id,
            novel_id=t.novel_id,
            event_id=t.event_id,
            sequence=t.sequence,
            event=event_to_timeline_dict(t.event) if t.event else None,
        )
        for t in timelines
    ]


@router.post("", response_model=TimelineOut, status_code=201)
def create_timeline(payload: TimelineCreate, db: Session = Depends(get_db)):
    item = Timeline(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{timeline_id}", response_model=TimelineOut)
def get_timeline(timeline_id: str, db: Session = Depends(get_db)):
    return get_or_404(db, Timeline, timeline_id)


@router.put("/{timeline_id}", response_model=TimelineOut)
def update_timeline(timeline_id: str, payload: TimelineUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, Timeline, timeline_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{timeline_id}", status_code=204)
def delete_timeline(timeline_id: str, db: Session = Depends(get_db)):
    item = get_or_404(db, Timeline, timeline_id)
    db.delete(item)
    db.commit()
