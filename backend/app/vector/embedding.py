from functools import lru_cache
import threading

from sentence_transformers import SentenceTransformer

from app.config import get_settings

_embed_lock = threading.Lock()


@lru_cache
def get_embedding_model() -> SentenceTransformer:
    settings = get_settings()
    return SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> list[float]:
    if not text.strip():
        return []
    with _embed_lock:
        model = get_embedding_model()
        vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()
