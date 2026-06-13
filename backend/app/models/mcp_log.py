from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class McpCallLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "mcp_call_logs"

    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    arguments: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
