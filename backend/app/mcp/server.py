import json
import logging

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from mcp.types import TextContent, Tool
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from app.database import SessionLocal
from app.mcp.logging import log_mcp_call
from app.mcp.tools import MCP_TOOLS, TOOL_MAP

logger = logging.getLogger(__name__)

mcp_server = Server("NovelOS MCP")
sse_transport = SseServerTransport("/mcp/messages/")
session_manager = StreamableHTTPSessionManager(
    app=mcp_server,
    stateless=True,
    json_response=False,
)


class McpHttpHandler:
    """Raw ASGI handler for Streamable HTTP.

    Must be a class instance (not a function) so Starlette skips the
    request_response() wrapper that expects a Response return value.
    session_manager.handle_request() writes via ASGI send and returns None.
    """

    def __init__(self, manager: StreamableHTTPSessionManager) -> None:
        self._manager = manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self._manager.handle_request(scope, receive, send)


class McpMessagesHandler:
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await sse_transport.handle_post_message(scope, receive, send)


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name=tool.name,
            description=tool.description,
            inputSchema=tool.input_schema,
        )
        for tool in MCP_TOOLS
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    tool = TOOL_MAP.get(name)
    if not tool:
        raise ValueError(f"Unknown tool: {name}")

    db = SessionLocal()
    try:
        result = tool.handler(db, arguments)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except Exception as exc:
        log_mcp_call(db, name, arguments, False, error_message=str(exc))
        raise
    finally:
        db.close()


async def handle_sse(request: Request) -> Response:
    async with sse_transport.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp_server.run(
            streams[0],
            streams[1],
            mcp_server.create_initialization_options(),
        )
    return Response()


def create_mcp_routes() -> list:
    return [
        Route(
            "/mcp/http",
            endpoint=McpHttpHandler(session_manager),
            methods=["GET", "POST", "DELETE"],
        ),
        Route("/mcp/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/mcp/messages", app=McpMessagesHandler()),
    ]
