from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "NovelOS"
    debug: bool = True
    database_url: str = "sqlite:///./novelos.db"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "novelos"
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    vector_top_k: int = 10
    writing_rules_file: str = "data/writing_rules.md"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    mcp_api_key: str = ""
    mcp_require_auth: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
