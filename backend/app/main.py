from __future__ import annotations

import json
from typing import Any

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agent import handle_cancel, handle_chat, handle_confirm, iter_chat_events
from app.config import get_settings
from app.db import get_db, init_db
from app.demo_pos import DemoPosAdapter
from app.errors import AppError
from app.llm import clear_llm_overlay, ping_llm, public_llm_status, put_llm_overlay, resolve_llm
from app.pos_port import PosPort
from app.threads import archive_thread, get_thread_public, list_threads

app = FastAPI(title="Desk assistant demo", version="0.1.0")
_pos: PosPort = DemoPosAdapter()


def get_pos() -> PosPort:
    return _pos


@app.on_event("startup")
def _startup() -> None:
    init_db()


origins = [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
def _app_error(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse({"ok": False, "error": exc.message}, status_code=exc.status_code)


def ok(data: Any) -> dict[str, Any]:
    return {"ok": True, "data": data}


class ChatIn(BaseModel):
    messages: list[dict[str, Any]] = Field(default_factory=list)
    thread_id: int | None = None


class ConfirmIn(BaseModel):
    preview_id: str


class LlmIn(BaseModel):
    api_key: str | None = None
    base_url: str | None = None
    model: str | None = None
    clear: bool = False


@app.get("/api/v1/health")
def health() -> dict[str, Any]:
    return ok({"status": "ok", "demo": True})


@app.get("/api/v1/settings/llm")
def settings_get(db: Session = Depends(get_db)) -> dict[str, Any]:
    return ok(public_llm_status(db))


@app.post("/api/v1/settings/llm/test")
def settings_test(body: LlmIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    creds = resolve_llm(db)
    ping_llm(
        api_key=(body.api_key or creds.api_key),
        base_url=(body.base_url or creds.base_url),
        model=(body.model or creds.model),
    )
    return ok({"ok": True})


@app.put("/api/v1/settings/llm")
def settings_put(body: LlmIn, db: Session = Depends(get_db)) -> dict[str, Any]:
    if body.clear:
        return ok(clear_llm_overlay(db))
    return ok(
        put_llm_overlay(
            db,
            api_key=body.api_key,
            base_url=body.base_url,
            model=body.model,
        )
    )


@app.get("/api/v1/agent/threads")
def threads_list(db: Session = Depends(get_db)) -> dict[str, Any]:
    return ok(list_threads(db))


@app.get("/api/v1/agent/threads/{thread_id}")
def threads_get(thread_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    return ok(get_thread_public(db, thread_id))


@app.delete("/api/v1/agent/threads/{thread_id}")
def threads_del(thread_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    archive_thread(db, thread_id)
    return ok({"archived": True})


@app.post("/api/v1/agent/chat")
def chat(body: ChatIn, db: Session = Depends(get_db), pos: PosPort = Depends(get_pos)) -> dict[str, Any]:
    return ok(handle_chat(db, pos, body.messages, body.thread_id))


@app.post("/api/v1/agent/chat/stream")
def chat_stream(body: ChatIn, db: Session = Depends(get_db), pos: PosPort = Depends(get_pos)):
    def events():
        try:
            for ev in iter_chat_events(db, pos, messages=body.messages, thread_id=body.thread_id):
                yield f"data: {json.dumps(ev, ensure_ascii=False)}\n\n"
        except AppError as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': exc.message}, ensure_ascii=False)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@app.post("/api/v1/agent/confirm")
def confirm(body: ConfirmIn, db: Session = Depends(get_db), pos: PosPort = Depends(get_pos)) -> dict[str, Any]:
    return ok(handle_confirm(db, pos, body.preview_id))


@app.post("/api/v1/agent/cancel-preview")
def cancel(body: ConfirmIn) -> dict[str, Any]:
    return ok(handle_cancel(body.preview_id))
