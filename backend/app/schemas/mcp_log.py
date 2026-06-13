from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMBase


class McpCallLogOut(ORMBase):
    id: str
    tool_name: str
    arguments: str | None
    result_summary: str | None
    success: bool
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class McpEndpointOut(BaseModel):
    transport: str
    endpoint: str
    description: str


class McpStatusOut(BaseModel):
    status: str
    auth_enabled: bool
    api_key: str | None = None
    api_key_hint: str | None = None
    endpoints: list[McpEndpointOut]
    tools: list[str]


class McpApiKeyOut(BaseModel):
    api_key: str
