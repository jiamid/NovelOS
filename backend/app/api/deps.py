from typing import TypeVar

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import Base

ModelT = TypeVar("ModelT", bound=Base)


def get_or_404(db: Session, model: type[ModelT], item_id: str) -> ModelT:
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return item
