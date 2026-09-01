from __future__ import annotations

import secrets
import time
from dataclasses import asdict, dataclass, field
from typing import Any

from app.pos_port import WritePreview

TTL_SECONDS = 180
_STORE: dict[str, tuple[dict[str, Any], float]] = {}


@dataclass
class PendingPreview:
    preview_id: str
    tool_name: str
    title: str
    message: str
    compare_rows: list[dict[str, str]] = field(default_factory=list)
    wired: bool = False


def put_preview(preview: WritePreview) -> PendingPreview:
    pid = secrets.token_urlsafe(12)
    row = PendingPreview(
        preview_id=pid,
        tool_name=preview.tool_name,
        title=preview.title,
        message=preview.message,
        compare_rows=preview.compare_rows,
        wired=preview.wired,
    )
    _STORE[pid] = (asdict(row), time.time() + TTL_SECONDS)
    return row


def get_preview(preview_id: str) -> dict[str, Any]:
    item = _STORE.get(preview_id)
    if not item:
        from app.errors import AppError

        raise AppError("确认卡已过期，请再问一次", 404)
    payload, exp = item
    if time.time() > exp:
        _STORE.pop(preview_id, None)
        from app.errors import AppError

        raise AppError("确认卡已过期，请再问一次", 404)
    return payload


def drop_preview(preview_id: str) -> None:
    _STORE.pop(preview_id, None)
