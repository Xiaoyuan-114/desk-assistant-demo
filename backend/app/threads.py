from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import AppError
from app.llm import dump_json
from app.models import AgentMessage, AgentThread

TITLE_CHARS = 16
_KEY_RE = re.compile(r"sk-[A-Za-z0-9_\-]{8,}")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def thread_title_from(text: str) -> str:
    compact = "".join((text or "").split())
    if compact in {"确认", "好的", "确定", "是"}:
        return ""
    return compact[:TITLE_CHARS]


def resolve_thread(db: Session, thread_id: int | None, user_text: str) -> AgentThread:
    if thread_id is not None:
        thread = db.get(AgentThread, thread_id)
        if thread is None or thread.archived:
            raise AppError("对话不存在或已删除", 404)
        return thread
    now = now_utc()
    thread = AgentThread(title=thread_title_from(user_text), created_at=now, updated_at=now)
    db.add(thread)
    db.flush()
    return thread


def persist_turn(
    db: Session,
    thread: AgentThread,
    *,
    user_text: str,
    reply: str,
    pending: dict[str, Any] | None = None,
    error: bool = False,
    visuals: list[dict[str, Any]] | None = None,
) -> None:
    if _KEY_RE.search(user_text or "") or _KEY_RE.search(reply or ""):
        raise AppError("对话不能保存密钥", 500)
    blob = None
    if pending or visuals:
        payload = dict(pending or {})
        if visuals:
            payload["visuals"] = visuals
        blob = dump_json(payload)
        if _KEY_RE.search(blob):
            raise AppError("对话不能保存密钥", 500)
    now = now_utc()
    db.add(AgentMessage(thread_id=thread.id, role="user", text=user_text, created_at=now))
    db.add(
        AgentMessage(
            thread_id=thread.id,
            role="assistant",
            text=reply,
            pending_json=blob,
            error=error,
            created_at=now,
        )
    )
    if not thread.title:
        thread.title = thread_title_from(user_text)
    thread.updated_at = now
    db.commit()


def list_threads(db: Session) -> list[dict[str, Any]]:
    rows = db.scalars(
        select(AgentThread)
        .where(AgentThread.archived.is_(False))
        .order_by(AgentThread.updated_at.desc())
        .limit(50)
    ).all()
    return [
        {
            "id": row.id,
            "title": row.title or "未命名",
            "updated_at": row.updated_at.isoformat() if row.updated_at else "",
        }
        for row in rows
    ]


def get_thread_public(db: Session, thread_id: int) -> dict[str, Any]:
    thread = db.get(AgentThread, thread_id)
    if thread is None or thread.archived:
        raise AppError("对话不存在或已删除", 404)
    messages = []
    for msg in thread.messages:
        pending = None
        if msg.pending_json:
            try:
                pending = json.loads(msg.pending_json)
            except json.JSONDecodeError:
                pending = None
        messages.append(
            {
                "id": msg.id,
                "role": msg.role,
                "text": msg.text,
                "error": msg.error,
                "pending": pending,
            }
        )
    return {"id": thread.id, "title": thread.title, "messages": messages}


def archive_thread(db: Session, thread_id: int) -> None:
    thread = db.get(AgentThread, thread_id)
    if thread is None:
        raise AppError("对话不存在或已删除", 404)
    thread.archived = True
    db.commit()
