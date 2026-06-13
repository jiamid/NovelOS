from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_or_404
from app.database import get_db
from app.models.event import Event
from app.schemas.common import PaginatedResponse
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services.event_service import event_to_out, sync_event_characters

router = APIRouter(prefix="/event", tags=["event"])

_EVENT_LOAD = (joinedload(Event.characters),)


@router.get("", response_model=PaginatedResponse[EventOut])
def list_events(
    novel_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Event).options(*_EVENT_LOAD)
    if novel_id:
        query = query.where(Event.novel_id == novel_id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size))
        .unique()
        .scalars()
        .all()
    )
    return PaginatedResponse(
        items=[event_to_out(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    character_ids = data.pop("character_ids", [])
    item = Event(**data)
    db.add(item)
    db.flush()
    sync_event_characters(db, item, character_ids)
    db.commit()
    db.refresh(item)
    item = (
        db.execute(select(Event).options(*_EVENT_LOAD).where(Event.id == item.id))
        .unique()
        .scalar_one()
    )
    return event_to_out(item)


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: str, db: Session = Depends(get_db)):
    get_or_404(db, Event, event_id)
    item = (
        db.execute(select(Event).options(*_EVENT_LOAD).where(Event.id == event_id))
        .unique()
        .scalar_one()
    )
    return event_to_out(item)


@router.put("/{event_id}", response_model=EventOut)
def update_event(event_id: str, payload: EventUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, Event, event_id)
    data = payload.model_dump(exclude_unset=True)
    character_ids = data.pop("character_ids", None)
    for key, value in data.items():
        setattr(item, key, value)
    sync_event_characters(db, item, character_ids)
    db.commit()
    item = (
        db.execute(select(Event).options(*_EVENT_LOAD).where(Event.id == event_id))
        .unique()
        .scalar_one()
    )
    return event_to_out(item)


@router.delete("/{event_id}", status_code=204)
def delete_event(event_id: str, db: Session = Depends(get_db)):
    item = get_or_404(db, Event, event_id)
    db.delete(item)
    db.commit()
