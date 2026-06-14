from fastapi import APIRouter

from app.api import (
    chapter,
    character,
    dashboard,
    event,
    mcp_log,
    novel,
    timeline,
    writing_rules,
)

api_router = APIRouter(prefix="/api")
api_router.include_router(novel.router)
api_router.include_router(chapter.router)
api_router.include_router(character.router)
api_router.include_router(event.router)
api_router.include_router(timeline.router)
api_router.include_router(dashboard.router)
api_router.include_router(mcp_log.router)
api_router.include_router(writing_rules.router)
