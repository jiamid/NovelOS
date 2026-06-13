import logging
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import get_settings
from app.vector.embedding import embed_text

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.collection = settings.qdrant_collection
        self.client = QdrantClient(
            url=settings.qdrant_url,
            check_compatibility=False,
            # Avoid routing localhost through system HTTP proxy (breaks Qdrant).
            trust_env=False,
        )
        self._initialized = False

    def ensure_collection(self) -> None:
        if self._initialized:
            return
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection for c in collections)
            if not exists:
                sample = embed_text("init")
                size = len(sample) if sample else 384
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=qmodels.VectorParams(size=size, distance=qmodels.Distance.COSINE),
                )
            self._initialized = True
        except Exception as exc:
            logger.warning("Qdrant not available, vector search disabled: %s", exc)
            self._initialized = False

    @property
    def available(self) -> bool:
        return self._initialized

    def upsert(
        self,
        entity_type: str,
        entity_id: str,
        novel_id: str,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.ensure_collection()
        if not self._initialized or not text.strip():
            return
        vector = embed_text(text)
        if not vector:
            return
        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "novel_id": novel_id,
            "text": text[:2000],
            **(metadata or {}),
        }
        # Qdrant accepts UUID or uint; entity_id is already a UUID string.
        self.client.upsert(
            collection_name=self.collection,
            points=[
                qmodels.PointStruct(
                    id=entity_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

    def delete(self, entity_type: str, entity_id: str) -> None:
        if not self._initialized:
            return
        self.client.delete(
            collection_name=self.collection,
            points_selector=qmodels.PointIdsList(points=[entity_id]),
        )

    def delete_by_novel(self, novel_id: str) -> None:
        self.ensure_collection()
        if not self._initialized:
            return
        self.client.delete(
            collection_name=self.collection,
            points_selector=qmodels.FilterSelector(
                filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="novel_id",
                            match=qmodels.MatchValue(value=novel_id),
                        )
                    ]
                )
            ),
        )

    def search(
        self,
        query: str,
        novel_id: str | None = None,
        entity_type: str | None = None,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        self.ensure_collection()
        if not self._initialized or not query.strip():
            return []
        settings = get_settings()
        vector = embed_text(query)
        if not vector:
            return []
        must: list[qmodels.FieldCondition] = []
        if novel_id:
            must.append(
                qmodels.FieldCondition(
                    key="novel_id",
                    match=qmodels.MatchValue(value=novel_id),
                )
            )
        if entity_type:
            must.append(
                qmodels.FieldCondition(
                    key="entity_type",
                    match=qmodels.MatchValue(value=entity_type),
                )
            )
        query_filter = qmodels.Filter(must=must) if must else None
        response = self.client.query_points(
            collection_name=self.collection,
            query=vector,
            query_filter=query_filter,
            limit=top_k or settings.vector_top_k,
        )
        return [
            {
                "score": hit.score,
                "entity_type": (hit.payload or {}).get("entity_type"),
                "entity_id": (hit.payload or {}).get("entity_id"),
                "text": (hit.payload or {}).get("text"),
                "metadata": {
                    k: v
                    for k, v in (hit.payload or {}).items()
                    if k not in {"entity_type", "entity_id", "text", "novel_id", "universe_id"}
                },
            }
            for hit in response.points
        ]


_vector_store: VectorStore | None = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
