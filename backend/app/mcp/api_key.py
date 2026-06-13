import secrets
from pathlib import Path

from app.config import get_settings

_KEY_FILE = Path(__file__).resolve().parents[2] / "data" / "mcp_api_key"


def _ensure_key_file() -> str:
    settings = get_settings()
    if settings.mcp_api_key:
        return settings.mcp_api_key

    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    if _KEY_FILE.exists():
        return _KEY_FILE.read_text(encoding="utf-8").strip()

    key = secrets.token_urlsafe(32)
    _KEY_FILE.write_text(key, encoding="utf-8")
    return key


def get_mcp_api_key() -> str:
    return _ensure_key_file()


def regenerate_mcp_api_key() -> str:
    key = secrets.token_urlsafe(32)
    _KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
    _KEY_FILE.write_text(key, encoding="utf-8")
    return key


def is_auth_enabled() -> bool:
    settings = get_settings()
    return settings.mcp_require_auth


def verify_api_key(provided: str | None) -> bool:
    if not is_auth_enabled():
        return True
    if not provided:
        return False
    return secrets.compare_digest(provided, get_mcp_api_key())


def extract_api_key_from_headers(headers: dict) -> str | None:
    auth = headers.get("authorization") or headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return headers.get("x-api-key") or headers.get("X-API-Key")
