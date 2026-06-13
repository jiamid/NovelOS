from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.mcp.api_key import extract_api_key_from_headers, is_auth_enabled, verify_api_key


class McpApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/mcp"):
            return await call_next(request)

        if not is_auth_enabled():
            return await call_next(request)

        provided = extract_api_key_from_headers(dict(request.headers))
        if not verify_api_key(provided):
            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid or missing API key. Use Authorization: Bearer <key> or X-API-Key header."
                },
            )
        return await call_next(request)
