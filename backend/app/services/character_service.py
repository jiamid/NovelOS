from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.character import Character
from app.utils.serialization import character_to_dict
from app.vector.store import get_vector_store


def assert_unique_character_name(
    db: Session,
    novel_id: str,
    name: str,
    exclude_id: str | None = None,
) -> None:
    normalized = name.strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="人物姓名不能为空")

    query = select(Character.id).where(
        Character.novel_id == novel_id,
        Character.name == normalized,
    )
    if exclude_id:
        query = query.where(Character.id != exclude_id)
    exists = db.scalar(query.limit(1))
    if exists:
        raise HTTPException(status_code=409, detail=f"该小说下已存在人物「{normalized}」")


def search_character(
    db: Session,
    keyword: str,
    novel_id: str | None = None,
    limit: int = 20,
) -> list[dict]:
    from sqlalchemy import or_

    like = f"%{keyword}%"
    query = select(Character).where(
        or_(Character.name.ilike(like), Character.description.ilike(like))
    )
    if novel_id:
        query = query.where(Character.novel_id == novel_id)
    sql_results = db.execute(query.limit(limit)).scalars().all()
    results = {c.id: character_to_dict(c) for c in sql_results}

    vector_hits = get_vector_store().search(
        query=keyword,
        novel_id=novel_id,
        entity_type="character",
        top_k=limit,
    )
    for hit in vector_hits:
        entity_id = hit.get("entity_id")
        if entity_id and entity_id not in results:
            character = db.get(Character, entity_id)
            if character:
                item = character_to_dict(character)
                item["score"] = hit.get("score")
                results[entity_id] = item

    return list(results.values())[:limit]
