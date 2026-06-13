from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_or_404
from app.database import get_db
from app.models.character import Character, CharacterRelation
from app.schemas.character import (
    CharacterCreate,
    CharacterOut,
    CharacterRelationCreate,
    CharacterRelationOut,
    CharacterUpdate,
)
from app.schemas.common import PaginatedResponse
from app.services.character_service import assert_unique_character_name
from app.services.indexing_tasks import schedule_index_character
from app.utils.serialization import character_to_dict

router = APIRouter(prefix="/character", tags=["character"])


def _to_out(character: Character) -> CharacterOut:
    data = character_to_dict(character)
    return CharacterOut(**data, created_at=character.created_at, updated_at=character.updated_at)


@router.get("", response_model=PaginatedResponse[CharacterOut])
def list_characters(
    novel_id: str | None = None,
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = select(Character)
    if novel_id:
        query = query.where(Character.novel_id == novel_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.where(
            or_(Character.name.ilike(like), Character.description.ilike(like))
        )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return PaginatedResponse(
        items=[_to_out(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("", response_model=CharacterOut, status_code=201)
def create_character(
    payload: CharacterCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    data = payload.model_dump()
    name = data["name"].strip()
    assert_unique_character_name(db, data["novel_id"], name)
    abilities = data.pop("abilities", [])
    tags = data.pop("tags", [])
    data["name"] = name
    item = Character(**data)
    item.abilities_list = abilities
    item.tags_list = tags
    db.add(item)
    db.commit()
    db.refresh(item)
    background_tasks.add_task(schedule_index_character, item.id)
    return _to_out(item)


@router.get("/{character_id}", response_model=CharacterOut)
def get_character(character_id: str, db: Session = Depends(get_db)):
    return _to_out(get_or_404(db, Character, character_id))


@router.put("/{character_id}", response_model=CharacterOut)
def update_character(
    character_id: str,
    payload: CharacterUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    item = get_or_404(db, Character, character_id)
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        data["name"] = data["name"].strip()
        assert_unique_character_name(db, item.novel_id, data["name"], exclude_id=character_id)
    if "abilities" in data:
        item.abilities_list = data.pop("abilities") or []
    if "tags" in data:
        item.tags_list = data.pop("tags") or []
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    background_tasks.add_task(schedule_index_character, item.id)
    return _to_out(item)


@router.delete("/{character_id}", status_code=204)
def delete_character(character_id: str, db: Session = Depends(get_db)):
    item = get_or_404(db, Character, character_id)
    db.delete(item)
    db.commit()


@router.post("/relation", response_model=CharacterRelationOut, status_code=201)
def create_relation(payload: CharacterRelationCreate, db: Session = Depends(get_db)):
    item = CharacterRelation(**payload.model_dump())
    db.add(item)
    db.commit()
    return item


@router.get("/relation/list", response_model=list[CharacterRelationOut])
def list_relations(novel_id: str, db: Session = Depends(get_db)):
    chars = db.execute(
        select(Character.id).where(Character.novel_id == novel_id)
    ).scalars().all()
    if not chars:
        return []
    return db.execute(
        select(CharacterRelation).where(CharacterRelation.source_id.in_(chars))
    ).scalars().all()


@router.delete("/relation", status_code=204)
def delete_relation(source_id: str, target_id: str, db: Session = Depends(get_db)):
    item = db.get(CharacterRelation, (source_id, target_id))
    if not item:
        raise HTTPException(status_code=404, detail="关系不存在")
    db.delete(item)
    db.commit()
