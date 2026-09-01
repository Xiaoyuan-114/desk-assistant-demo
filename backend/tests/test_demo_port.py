from app.agent import _complete_reads, _reply_facts
from app.demo_pos import DemoPosAdapter
from app.tools import execute_read, visual_from_read


def test_demo_today_has_no_shop_ledger_fields() -> None:
    data = DemoPosAdapter().today()
    assert data["demo"] is True
    assert "today_total_revenue" in data
    assert "order_no" not in data
    blob = str(data)
    assert "美团" not in blob
    assert "蘑菇" not in blob


def test_seats_are_stub_not_a_map() -> None:
    data = execute_read(DemoPosAdapter(), "seat_occupancy", {})
    assert data["wired"] is False
    assert "occupancy" not in data
    visual = visual_from_read("seat_occupancy", data)
    assert visual and visual["kind"] == "seats_stub"


def test_triple_read_fills_charts_without_llm() -> None:
    pos = DemoPosAdapter()
    text = "今天营业额是多少\n主要以什么方式支付\n开台时段主要是什么"
    visuals, today = _complete_reads(pos, text, [], set(), None)
    kinds = {v["kind"] for v in visuals}
    assert kinds == {"pay_mix", "traffic"}
    reply = _reply_facts("图表已生成。", text, today)
    assert today and today["today_total_revenue"] in reply
    assert "元" in reply
    assert reply.strip() != "图表已生成。"
