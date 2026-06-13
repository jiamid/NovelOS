from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.mcp.api_key import get_mcp_api_key, is_auth_enabled, regenerate_mcp_api_key
from app.models.mcp_log import McpCallLog
from app.mcp.tools import MCP_TOOLS
from app.schemas.common import PaginatedResponse
from app.schemas.mcp_log import McpApiKeyOut, McpCallLogOut, McpEndpointOut, McpStatusOut

router = APIRouter(prefix="/mcp", tags=["mcp"])


@router.get("/status", response_model=McpStatusOut)
def mcp_status():
    key = get_mcp_api_key() if is_auth_enabled() else None
    return McpStatusOut(
        status="running",
        auth_enabled=is_auth_enabled(),
        api_key=key,
        api_key_hint=f"...{key[-6:]}" if key else None,
        endpoints=[
            McpEndpointOut(
                transport="streamable-http",
                endpoint="/mcp/http",
                description="MCP Streamable HTTP（推荐，支持 API Key）",
            ),
            McpEndpointOut(
                transport="sse",
                endpoint="/mcp/sse",
                description="MCP SSE（Cherry Studio 等）",
            ),
        ],
        tools=[tool.name for tool in MCP_TOOLS],
    )


@router.get("/api-key", response_model=McpApiKeyOut)
def get_api_key():
    return McpApiKeyOut(api_key=get_mcp_api_key())


@router.post("/api-key/regenerate", response_model=McpApiKeyOut)
def regenerate_api_key():
    return McpApiKeyOut(api_key=regenerate_mcp_api_key())


@router.get("/logs", response_model=PaginatedResponse[McpCallLogOut])
def list_mcp_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = select(McpCallLog).order_by(McpCallLog.created_at.desc())
    total = db.scalar(select(func.count()).select_from(McpCallLog)) or 0
    items = (
        db.execute(query.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)
