"""In-memory demo numbers. Not a ledger. Writes are intentionally unwired."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.pos_port import WritePreview

# Fictional weekday pattern. Not copied from any shop.
_TODAY_REVENUE = "1280.00"
_PAY_MIX = {
    "cash": {"amount": "320.00", "ratio": 0.25},
    "scan": {"amount": "768.00", "ratio": 0.60},
    "card": {"amount": "192.00", "ratio": 0.15},
}
_TRAFFIC_HOURS = [0, 0, 0, 1, 2, 4, 7, 5, 3, 2, 3, 4, 2, 1, 0]


class DemoPosAdapter:
    def today(self) -> dict[str, Any]:
        return {
            "demo": True,
            "today_total_revenue": _TODAY_REVENUE,
            "today_order_count": 18,
            "payment_mix": _PAY_MIX,
        }

    def trend(self, days: int = 7) -> dict[str, Any]:
        days = 30 if days >= 30 else 7
        start = date.today() - timedelta(days=days - 1)
        wave = [0.7, 0.9, 1.1, 0.8, 1.2, 1.4, 1.0]
        points = []
        for i in range(days):
            day = start + timedelta(days=i)
            factor = wave[i % 7]
            points.append(
                {
                    "date": day.isoformat(),
                    "total_revenue": f"{round(980 * factor, 2):.2f}",
                }
            )
        return {"demo": True, "days": days, "points": points}

    def traffic(self) -> dict[str, Any]:
        hours = [{"hour": 8 + i, "open_count": n} for i, n in enumerate(_TRAFFIC_HOURS)]
        return {"demo": True, "hours": hours}

    def seats(self) -> dict[str, Any]:
        return {
            "wired": False,
            "kind": "seats_stub",
            "title": "座位图",
            "message": "座位图未接入。请实现 PosPort.seats（例如对接柜台的座位占用查询）后，这里会展示座位图。演示仓不包含选座界面。",
        }

    def preview_write(self, tool_name: str, arguments: dict[str, Any]) -> WritePreview:
        labels = {
            "create_order": "开台",
            "settle_order": "结算",
            "update_package_price": "改套餐价",
            "change_seat": "换座",
        }
        title = labels.get(tool_name, tool_name)
        return WritePreview(
            tool_name=tool_name,
            title=title,
            message=f"「{title}」未接入真实柜台。请实现 PosPort.preview_write / confirm_write。点确认不会改任何账。",
            compare_rows=[
                {"label": "动作", "old": "—", "new": title},
                {"label": "接入状态", "old": "—", "new": "未接入"},
            ],
            wired=False,
        )

    def confirm_write(self, preview: WritePreview) -> dict[str, Any]:
        return {
            "ok": True,
            "wired": False,
            "message": f"未接入 POS，未执行「{preview.title}」。",
        }
