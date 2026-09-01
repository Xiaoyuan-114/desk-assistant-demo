from __future__ import annotations

import json
from typing import Any

from app.errors import AppError
from app.pos_port import PosPort

READ_TOOLS = frozenset(
    {"dashboard_today", "dashboard_trend", "dashboard_traffic", "seat_occupancy"}
)
WRITE_TOOLS = frozenset(
    {"create_order", "settle_order", "update_package_price", "change_seat"}
)


def openai_tools() -> list[dict[str, Any]]:
    def fn(name: str, description: str, props: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {"type": "object", "properties": props},
            },
        }

    return [
        fn("dashboard_today", "今日营业演示数字与支付构成。", {}),
        fn("dashboard_trend", "近几日营收趋势（演示数据）。", {"days": {"type": "integer"}}),
        fn("dashboard_traffic", "今日开台时段（演示数据）。", {}),
        fn("seat_occupancy", "座位占用。演示未接入，只返回占位说明。", {}),
        fn("create_order", "开台。演示未接入真实柜台。", {}),
        fn("settle_order", "结算。演示未接入真实柜台。", {}),
        fn("update_package_price", "改套餐价。演示未接入真实柜台。", {}),
        fn("change_seat", "换座。演示未接入真实柜台。", {}),
    ]


def _parse_args(arguments: Any) -> dict[str, Any]:
    if isinstance(arguments, dict):
        return arguments
    if isinstance(arguments, str) and arguments.strip():
        try:
            data = json.loads(arguments)
        except json.JSONDecodeError:
            return {}
        return data if isinstance(data, dict) else {}
    return {}


def execute_read(pos: PosPort, name: str, arguments: Any) -> dict[str, Any]:
    args = _parse_args(arguments)
    if name == "dashboard_today":
        return pos.today()
    if name == "dashboard_trend":
        return pos.trend(int(args.get("days") or 7))
    if name == "dashboard_traffic":
        return pos.traffic()
    if name == "seat_occupancy":
        return pos.seats()
    raise AppError(f"未注册的只读工具：{name}", 400)


def visual_from_read(name: str, data: dict[str, Any]) -> dict[str, Any] | None:
    if name == "dashboard_trend":
        return {"kind": "trend", "title": f"近{data.get('days') or 7}日营收（演示）", "data": data}
    if name == "dashboard_traffic":
        return {"kind": "traffic", "title": "时段客流（演示）", "data": data}
    if name == "dashboard_today":
        mix = data.get("payment_mix")
        if not mix:
            return None
        return {"kind": "pay_mix", "title": "支付构成（演示）", "data": {"payment_mix": mix}}
    if name == "seat_occupancy":
        return {
            "kind": "seats_stub",
            "title": data.get("title") or "座位图",
            "data": data,
        }
    return None
