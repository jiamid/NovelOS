from sqlalchemy.orm import Session

from app.models.novel import Novel
from app.vector.store import get_vector_store


def delete_novel(db: Session, novel_id: str) -> None:
    novel = db.get(Novel, novel_id)
    if not novel:
        raise ValueError(f"Novel {novel_id} not found")

    get_vector_store().delete_by_novel(novel_id)
    db.delete(novel)
    db.commit()
