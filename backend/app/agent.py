from __future__ import annotations

import re
from collections.abc import Iterator
from typing import Any

from sqlalchemy.orm import Session

from app.errors import AppError
from app.llm import complete_chat, dump_json
from app.pos_port import PosPort
from app.preview import drop_preview, get_preview, put_preview
from app.threads import persist_turn, resolve_thread
from app.tools import (
    READ_TOOLS,
    WRITE_TOOLS,
    execute_read,
    openai_tools,
    visual_from_read,
)

SYSTEM_PROMPT = """你是柜台助手演示，嵌在一个占位收银台里。
规则：
1. 只使用已注册工具。不要编造 SQL，不要猜测金额。
2. 查营业、趋势、客流、支付：立刻调用对应只读工具。一句里问了几件只读的事，把对应工具在同一轮一起调。图由前端画；问到的数字必须写在回复里（营业额带「元」，支付点出占比最高的方式）。禁止只回复「图表已生成。」或「见图。」。
3. 座位图：调用 seat_occupancy。演示未接入真实座位，工具会返回占位说明，把说明转述给店员，不要假装已经画出座位。
4. 开台、结算、改价、换座：调用对应写入工具。服务端会弹出确认卡。演示未接入真实柜台，确认不会改库。不要让店员在对话框里打「确认」。
5. 用简洁中文回复。数字带单位。数据若来自演示适配器，可以提一句「这是演示数据」。
"""

_VERBAL_CONFIRM = frozenset({"确认", "好的", "确定", "确认执行", "是"})
_SALES_RE = re.compile(r"营业额|营收|卖了多少|进账|今天进了")
_PAY_MIX_RE = re.compile(
    r"支付来源|支付对比|支付占比|支付方式|方式支付|怎么付|哪种支付|现金还是|扫码多"
)
_TRAFFIC_RE = re.compile(r"客流|时段|哪个点人多|忙的时候")
_TREND_RE = re.compile(r"趋势|近\s*7\s*天|近\s*30")
_SEAT_RE = re.compile(r"座位图|进行中有哪些座|哪些座")
_PLACEHOLDERS = frozenset({"图表已生成。", "图表已生成", "见图。", "见图"})
MAX_ROUNDS = 4
MAX_MESSAGES = 20
PAY_LABELS = {"cash": "现金", "scan": "扫码", "card": "刷卡"}


def _last_user(messages: list[dict[str, Any]]) -> str:
    for row in reversed(messages):
        if row.get("role") == "user" and isinstance(row.get("content"), str):
            return row["content"]
    return ""


def _sanitize(messages: list[Any]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for row in messages:
        if not isinstance(row, dict):
            continue
        role, content = row.get("role"), row.get("content")
        if role not in ("user", "assistant") or not isinstance(content, str):
            continue
        text = content.strip()
        if not text:
            continue
        out.append({"role": role, "content": text})
    if not out:
        raise AppError("请输入要对助手说的话", 422)
    return out[-MAX_MESSAGES:]


def _intents(text: str) -> set[str]:
    found: set[str] = set()
    if _SALES_RE.search(text or ""):
        found.add("sales")
    if _PAY_MIX_RE.search(text or ""):
        found.add("pay")
    if _TRAFFIC_RE.search(text or ""):
        found.add("traffic")
    if _TREND_RE.search(text or ""):
        found.add("trend")
    if _SEAT_RE.search(text or ""):
        found.add("seats")
    return found


def _append_visual(visuals: list[dict[str, Any]], item: dict[str, Any] | None) -> None:
    if not item:
        return
    if item.get("kind") in {row.get("kind") for row in visuals}:
        return
    visuals.append(item)


def _complete_reads(
    pos: PosPort,
    user_text: str,
    visuals: list[dict[str, Any]],
    ran: set[str],
    today: dict[str, Any] | None,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    out = list(visuals)
    intents = _intents(user_text)
    need_today = "sales" in intents or "pay" in intents
    if need_today and today is None and "dashboard_today" not in ran:
        today = execute_read(pos, "dashboard_today", {})
        ran.add("dashboard_today")
    if need_today and today:
        _append_visual(out, visual_from_read("dashboard_today", today))
    if "traffic" in intents and not any(v.get("kind") == "traffic" for v in out):
        data = execute_read(pos, "dashboard_traffic", {})
        _append_visual(out, visual_from_read("dashboard_traffic", data))
    if "trend" in intents and not any(v.get("kind") == "trend" for v in out):
        days = 30 if "30" in (user_text or "") else 7
        data = execute_read(pos, "dashboard_trend", {"days": days})
        _append_visual(out, visual_from_read("dashboard_trend", data))
    if "seats" in intents and not any(v.get("kind") == "seats_stub" for v in out):
        data = execute_read(pos, "seat_occupancy", {})
        _append_visual(out, visual_from_read("seat_occupancy", data))
    return out, today


def _yuan(value: Any) -> str:
    return f"{value} 元" if "元" in str(value) else f"{value} 元"


def _top_pay(today: dict[str, Any] | None) -> str | None:
    if not today:
        return None
    mix = today.get("payment_mix") or {}
    best, ratio = None, -1.0
    for key in PAY_LABELS:
        slot = mix.get(key) or {}
        r = float(slot.get("ratio") or 0)
        if r > ratio:
            best, ratio = key, r
    if not best:
        return None
    return f"主要以{PAY_LABELS[best]}支付（约 {int(round(ratio * 100))}%）。"


def _reply_facts(reply: str, user_text: str, today: dict[str, Any] | None) -> str:
    intents = _intents(user_text)
    text = (reply or "").strip()
    parts: list[str] = []
    if "sales" in intents and today and today.get("today_total_revenue") is not None:
        amount = str(today["today_total_revenue"])
        if amount not in text:
            parts.append(f"今日营业额：{_yuan(amount)}（演示数据）。")
    if "pay" in intents:
        line = _top_pay(today)
        if line and line.rstrip("。") not in text:
            parts.append(line)
    if "seats" in intents and ("座位图未接入" not in text):
        if not text or text in _PLACEHOLDERS:
            parts.append("座位图未接入。请实现座位占用查询接口后，这里会展示座位图。")
    placeholder = (not text) or (text in _PLACEHOLDERS)
    if parts:
        extra = "".join(parts)
        return extra if placeholder else extra + text
    return text or "好的。"


def _finish(
    db: Session,
    *,
    thread_id: int | None,
    user_text: str,
    reply: str,
    pending: dict[str, Any] | None,
    visuals: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    thread = resolve_thread(db, thread_id, user_text)
    persist_turn(db, thread, user_text=user_text, reply=reply, pending=pending, visuals=visuals)
    return {
        "reply": reply,
        "thread_id": thread.id,
        "visuals": visuals or [],
        "pending_confirmation": pending,
    }


def iter_text_deltas(text: str, size: int = 4) -> Iterator[str]:
    if not text:
        return
    for i in range(0, len(text), max(1, size)):
        yield text[i : i + size]


def iter_chat_events(
    db: Session,
    pos: PosPort,
    *,
    messages: list[Any],
    thread_id: int | None = None,
) -> Iterator[dict[str, Any]]:
    cleaned = _sanitize(messages)
    user_text = _last_user(cleaned)
    if user_text.strip() in _VERBAL_CONFIRM:
        reply = "请点弹出确认卡片上的「确认」。在对话框里打「确认」不会改任何数据。"
        finished = _finish(
            db, thread_id=thread_id, user_text=user_text, reply=reply, pending=None, visuals=[]
        )
        yield {"type": "delta", "text": finished["reply"]}
        yield {"type": "done", "thread_id": finished["thread_id"], "reply": finished["reply"]}
        return

    llm_messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}, *cleaned]
    tools = openai_tools()
    last_text = ""
    visuals: list[dict[str, Any]] = []
    ran: set[str] = set()
    today: dict[str, Any] | None = None

    try:
        for _ in range(MAX_ROUNDS):
            result = complete_chat(llm_messages, tools, db)
            last_text = (result.get("content") or "").strip()
            calls = [c for c in (result.get("tool_calls") or []) if c.get("name")]
            if not calls:
                visuals, today = _complete_reads(pos, user_text, visuals, ran, today)
                reply = _reply_facts(last_text or "好的。", user_text, today)
                finished = _finish(
                    db,
                    thread_id=thread_id,
                    user_text=user_text,
                    reply=reply,
                    pending=None,
                    visuals=visuals,
                )
                if visuals:
                    yield {"type": "visuals", "visuals": visuals}
                for part in iter_text_deltas(finished["reply"]):
                    yield {"type": "delta", "text": part}
                yield {
                    "type": "done",
                    "thread_id": finished["thread_id"],
                    "reply": finished["reply"],
                    "visuals": visuals,
                }
                return

            llm_messages.append(
                {
                    "role": "assistant",
                    "content": last_text or None,
                    "tool_calls": [
                        {
                            "id": c.get("id") or f"call_{i}",
                            "type": "function",
                            "function": {
                                "name": c["name"],
                                "arguments": c.get("arguments")
                                if isinstance(c.get("arguments"), str)
                                else dump_json(c.get("arguments") or {}),
                            },
                        }
                        for i, c in enumerate(calls)
                    ],
                }
            )
            write_call = next((c for c in calls if c["name"] in WRITE_TOOLS), None)
            for call in calls:
                name = call["name"]
                args = call.get("arguments")
                yield {"type": "status", "text": "正在查看…"}
                if name in READ_TOOLS:
                    data = execute_read(pos, name, args)
                    ran.add(name)
                    if name == "dashboard_today":
                        today = data
                    visual = visual_from_read(name, data)
                    _append_visual(visuals, visual)
                    llm_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id") or name,
                            "content": dump_json(data),
                        }
                    )
                    continue
                if name in WRITE_TOOLS:
                    built = pos.preview_write(name, args if isinstance(args, dict) else {})
                    preview = put_preview(built)
                    pending = {
                        "preview_id": preview.preview_id,
                        "tool_name": preview.tool_name,
                        "title": preview.title,
                        "message": preview.message,
                        "compare_rows": preview.compare_rows,
                        "wired": preview.wired,
                    }
                    visuals, today = _complete_reads(pos, user_text, visuals, ran, today)
                    reply = _reply_facts(last_text or built.message, user_text, today)
                    finished = _finish(
                        db,
                        thread_id=thread_id,
                        user_text=user_text,
                        reply=reply,
                        pending=pending,
                        visuals=visuals,
                    )
                    yield {"type": "pending", "pending_confirmation": pending}
                    if visuals:
                        yield {"type": "visuals", "visuals": visuals}
                    for part in iter_text_deltas(finished["reply"]):
                        yield {"type": "delta", "text": part}
                    yield {
                        "type": "done",
                        "thread_id": finished["thread_id"],
                        "reply": finished["reply"],
                        "visuals": visuals,
                    }
                    return
                raise AppError(f"未注册的工具：{name}", 400)
            if write_call:
                continue

        visuals, today = _complete_reads(pos, user_text, visuals, ran, today)
        reply = _reply_facts(last_text or "请把问题再缩短一些。", user_text, today)
        finished = _finish(
            db, thread_id=thread_id, user_text=user_text, reply=reply, pending=None, visuals=visuals
        )
        if visuals:
            yield {"type": "visuals", "visuals": visuals}
        for part in iter_text_deltas(finished["reply"]):
            yield {"type": "delta", "text": part}
        yield {
            "type": "done",
            "thread_id": finished["thread_id"],
            "reply": finished["reply"],
            "visuals": visuals,
        }
    except AppError as exc:
        if exc.status_code == 503:
            raise
        visuals, today = _complete_reads(pos, user_text, visuals, ran, today)
        if visuals:
            reply = _reply_facts(last_text or "", user_text, today)
            finished = _finish(
                db,
                thread_id=thread_id,
                user_text=user_text,
                reply=reply,
                pending=None,
                visuals=visuals,
            )
            yield {"type": "visuals", "visuals": visuals}
            for part in iter_text_deltas(finished["reply"]):
                yield {"type": "delta", "text": part}
            yield {
                "type": "done",
                "thread_id": finished["thread_id"],
                "reply": finished["reply"],
                "visuals": visuals,
            }
            return
        raise


def handle_chat(db: Session, pos: PosPort, messages: list[Any], thread_id: int | None) -> dict[str, Any]:
    done = None
    pending = None
    for ev in iter_chat_events(db, pos, messages=messages, thread_id=thread_id):
        if ev.get("type") == "pending":
            pending = ev.get("pending_confirmation")
        elif ev.get("type") == "done":
            done = ev
    if done is None:
        raise AppError("助手没有返回内容", 502)
    return {
        "reply": done["reply"],
        "thread_id": done["thread_id"],
        "visuals": done.get("visuals") or [],
        "pending_confirmation": pending,
    }


def handle_confirm(db: Session, pos: PosPort, preview_id: str) -> dict[str, Any]:
    row = get_preview(preview_id)
    from app.pos_port import WritePreview

    result = pos.confirm_write(
        WritePreview(
            tool_name=row["tool_name"],
            title=row["title"],
            message=row["message"],
            compare_rows=row.get("compare_rows") or [],
            wired=bool(row.get("wired")),
        )
    )
    drop_preview(preview_id)
    return {"reply": result.get("message") or "未接入，未改数据。", "result": result}


def handle_cancel(preview_id: str) -> dict[str, Any]:
    drop_preview(preview_id)
    return {"cancelled": True, "preview_id": preview_id}
