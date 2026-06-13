import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.config import get_settings
from app.database import Base, engine
from app.db_migrate import run_migrations
from app.mcp.api_key import get_mcp_api_key, is_auth_enabled
from app.mcp.auth import McpApiKeyMiddleware
from app.mcp.server import create_mcp_routes, session_manager
from app.vector.embedding import get_embedding_model
from app.vector.store import get_vector_store

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
    try:
        get_vector_store().ensure_collection()
        logger.info("Vector store initialized")
    except Exception as exc:
        logger.warning("Vector store init skipped: %s", exc)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, get_embedding_model)
    logger.info("Embedding model preloaded")

    if is_auth_enabled():
        key = get_mcp_api_key()
        logger.info("MCP API key auth enabled (key suffix: ...%s)", key[-6:])

    async with session_manager.run():
        yield


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(McpApiKeyMiddleware)
app.include_router(api_router)

for route in create_mcp_routes():
    app.routes.insert(0, route)
