import json

from sqlalchemy.orm import Session

from app.models.mcp_log import McpCallLog


def log_mcp_call(
    db: Session,
    tool_name: str,
    arguments: dict,
    success: bool,
    result_summary: str | None = None,
    error_message: str | None = None,
) -> None:
    log = McpCallLog(
        tool_name=tool_name,
        arguments=json.dumps(arguments, ensure_ascii=False),
        result_summary=result_summary,
        success=success,
        error_message=error_message,
    )
    db.add(log)
    db.commit()
