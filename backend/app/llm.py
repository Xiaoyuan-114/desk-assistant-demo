from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx
from sqlalchemy.orm import Session

from app.config import get_settings
from app.errors import AppError
from app.models import AppSetting

KEY_URL = "llm_base_url"
KEY_MODEL = "llm_model"
KEY_API = "llm_api_key"


@dataclass(frozen=True)
class ResolvedLlm:
    api_key: str
    base_url: str
    model: str
    source: str


def _setting(db: Session | None, key: str) -> str:
    if db is None:
        return ""
    row = db.get(AppSetting, key)
    return (row.value if row else "") or ""


def resolve_llm(db: Session | None = None) -> ResolvedLlm:
    env = get_settings()
    shop_key = _setting(db, KEY_API).strip()
    shop_url = _setting(db, KEY_URL).strip()
    shop_model = _setting(db, KEY_MODEL).strip()
    api_key = shop_key or env.agent_llm_api_key.strip()
    base_url = shop_url or env.agent_llm_base_url.strip()
    model = shop_model or env.agent_llm_model.strip() or "deepseek-chat"
    if shop_key:
        source = "settings"
    elif env.agent_llm_api_key.strip():
        source = "env"
    else:
        source = "none"
    return ResolvedLlm(api_key=api_key, base_url=base_url, model=model, source=source)


def public_llm_status(db: Session | None = None) -> dict[str, Any]:
    creds = resolve_llm(db)
    last4 = creds.api_key[-4:] if len(creds.api_key) >= 4 else None
    return {
        "configured": bool(creds.api_key and creds.base_url),
        "source": creds.source,
        "last4": last4,
        "base_url": creds.base_url,
        "model": creds.model,
    }


def put_llm_overlay(
    db: Session,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    def write(key: str, value: str) -> None:
        row = db.get(AppSetting, key)
        if row is None:
            db.add(AppSetting(key=key, value=value))
        else:
            row.value = value

    if base_url is not None:
        write(KEY_URL, base_url.strip())
    if model is not None:
        write(KEY_MODEL, model.strip())
    if api_key is not None and api_key.strip():
        write(KEY_API, api_key.strip())
    db.commit()
    return public_llm_status(db)


def clear_llm_overlay(db: Session) -> dict[str, Any]:
    for key in (KEY_URL, KEY_MODEL, KEY_API):
        row = db.get(AppSetting, key)
        if row is not None:
            db.delete(row)
    db.commit()
    return public_llm_status(db)


def _completions_url(base: str) -> str:
    b = base.rstrip("/")
    if b.endswith("/chat/completions"):
        return b
    if b.endswith("/v1"):
        return f"{b}/chat/completions"
    return f"{b}/v1/chat/completions"


def _post(base_url: str, api_key: str, payload: dict[str, Any], timeout: float) -> httpx.Response:
    try:
        with httpx.Client(timeout=timeout) as client:
            return client.post(
                _completions_url(base_url),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.TimeoutException as exc:
        raise AppError("助手模型响应超时，请稍后重试", 504) from exc
    except httpx.HTTPError as exc:
        raise AppError("助手暂时连不上模型，请稍后重试", 502) from exc


def complete_chat(messages: list[dict[str, Any]], tools: list[dict[str, Any]], db: Session | None) -> dict[str, Any]:
    creds = resolve_llm(db)
    if not creds.api_key:
        raise AppError("请到设置填写密钥（或服务端 .env）", 503)
    if not creds.base_url:
        raise AppError("请到设置填写接口地址（或服务端 .env）", 503)
    payload: dict[str, Any] = {
        "model": creds.model,
        "messages": messages,
        "temperature": 0.2,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    timeout = float(get_settings().agent_llm_timeout_seconds or 45)
    res = _post(creds.base_url, creds.api_key, payload, timeout)
    if res.status_code >= 400:
        raise AppError(f"助手模型返回错误（{res.status_code}），请核对设置", 502)
    body = res.json()
    choices = body.get("choices") or []
    if not choices:
        raise AppError("助手模型没有返回内容", 502)
    message = (choices[0] or {}).get("message") or {}
    tool_calls = []
    for raw in message.get("tool_calls") or []:
        fn = raw.get("function") or {}
        tool_calls.append(
            {
                "id": raw.get("id") or "",
                "name": fn.get("name") or "",
                "arguments": fn.get("arguments") or "{}",
            }
        )
    return {"content": message.get("content") or "", "tool_calls": tool_calls}


def ping_llm(*, api_key: str, base_url: str, model: str) -> None:
    if not api_key.strip():
        raise AppError("请填写密钥后再测试", 400)
    if not base_url.strip():
        raise AppError("请填写接口地址后再测试", 400)
    timeout = min(float(get_settings().agent_llm_timeout_seconds or 45), 20.0)
    res = _post(
        base_url.strip(),
        api_key.strip(),
        {
            "model": (model or "deepseek-chat").strip() or "deepseek-chat",
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
            "temperature": 0,
        },
        timeout,
    )
    if res.status_code >= 400:
        raise AppError(f"测试未通过：模型接口返回 {res.status_code}", 400)
    if not (res.json().get("choices") or []):
        raise AppError("测试未通过：模型没有返回内容", 400)


def dump_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)
