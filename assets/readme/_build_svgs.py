# -*- coding: utf-8 -*-
from pathlib import Path

OUT = Path(__file__).resolve().parent

HERO = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="400" viewBox="0 0 1200 400" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <defs>
    <linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#ffe8d6"/>
      <stop offset="1" stop-color="#fff4e5"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="400" rx="26" fill="url(#wash)"/>
  <rect x="1" y="1" width="1198" height="398" rx="25" fill="none" stroke="#e4cdb0"/>
  <g id="title-block" transform="translate(64 72)">
    <text x="0" y="0" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="20">{eyebrow}</text>
    <text x="0" y="72" fill="#d62828" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="56" font-weight="700">{name}</text>
    <text x="0" y="124" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="22">{line1}</text>
    <text x="0" y="158" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="20">{line2}</text>
    <g transform="translate(0 196)">
      <rect width="112" height="36" rx="18" fill="#fffaf3" stroke="#e4cdb0"/>
      <text x="56" y="24" text-anchor="middle" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="18">{chip1}</text>
      <rect x="124" width="136" height="36" rx="18" fill="#fffaf3" stroke="#e4cdb0"/>
      <text x="192" y="24" text-anchor="middle" fill="#2b2118" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="18">Python 3.11</text>
      <rect x="272" width="116" height="36" rx="18" fill="#fffaf3" stroke="#e4cdb0"/>
      <text x="330" y="24" text-anchor="middle" fill="#2b2118" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="18">Node 20</text>
    </g>
  </g>
  <g id="project-proof" transform="translate(668 48)">
    <rect width="476" height="304" rx="20" fill="#fffaf3" stroke="#e4cdb0"/>
    <rect x="16" y="16" width="444" height="44" rx="14" fill="#fff4e5" stroke="#e4cdb0"/>
    <text x="32" y="44" fill="#d62828" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="16" font-weight="700">{name}</text>
    <rect x="156" y="24" width="72" height="28" rx="14" fill="#fffaf3" stroke="#e4cdb0"/>
    <text x="192" y="44" text-anchor="middle" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="18">{tab_orders}</text>
    <rect x="234" y="24" width="72" height="28" rx="14" fill="#d62828"/>
    <text x="270" y="44" text-anchor="middle" fill="#fffaf3" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="18">{tab_agent}</text>
    <rect x="312" y="24" width="72" height="28" rx="14" fill="#fffaf3" stroke="#e4cdb0"/>
    <text x="348" y="44" text-anchor="middle" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="18">{tab_settings}</text>
    <rect x="32" y="84" width="196" height="40" rx="12" fill="#ffe3e0"/>
    <text x="130" y="110" text-anchor="middle" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="18">{chip_sales}</text>
    <rect x="236" y="84" width="208" height="40" rx="12" fill="#fff4e5" stroke="#e4cdb0"/>
    <text x="340" y="110" text-anchor="middle" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="18">{chip_hours}</text>
    <rect x="32" y="140" width="412" height="132" rx="16" fill="#ffffff" stroke="#e4cdb0"/>
    <text x="52" y="176" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="16">{demo_label}</text>
    <text x="52" y="214" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="24" font-weight="700">{demo_amount}</text>
    <text x="52" y="248" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="16">{demo_note}</text>
  </g>
</svg>
"""

SECTION = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="128" viewBox="0 0 1200 128" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <rect width="1200" height="128" rx="22" fill="#fff4e5"/>
  <rect x="1" y="1" width="1198" height="126" rx="21" fill="none" stroke="#e4cdb0"/>
  <rect x="48" y="54" width="36" height="8" rx="4" fill="#d62828"/>
  <text x="100" y="48" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="40" font-weight="700">{title}</text>
  <text x="100" y="88" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="20">{sub}</text>
</svg>
"""

WORKFLOW = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="280" viewBox="0 0 1200 280" role="img" aria-labelledby="title desc">
  <title id="title">{title}</title>
  <desc id="desc">{desc}</desc>
  <rect width="1200" height="280" rx="26" fill="#fff4e5"/>
  <rect x="1" y="1" width="1198" height="278" rx="25" fill="none" stroke="#e4cdb0"/>
  <g transform="translate(40 40)">
    <rect width="340" height="200" rx="20" fill="#fffaf3" stroke="#e4cdb0"/>
    <text x="28" y="44" fill="#d62828" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="18">01</text>
    <text x="28" y="92" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="28" font-weight="700">{c1}</text>
    <text x="28" y="132" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="20">{c1a}</text>
    <text x="28" y="164" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="20">{c1b}</text>
  </g>
  <path d="M392 140 H428" stroke="#d62828" stroke-width="3"/>
  <path d="M418 130 L432 140 L418 150" fill="none" stroke="#d62828" stroke-width="3"/>
  <g transform="translate(440 40)">
    <rect width="340" height="200" rx="20" fill="#fffaf3" stroke="#e4cdb0"/>
    <text x="28" y="44" fill="#d62828" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="18">02</text>
    <text x="28" y="92" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="28" font-weight="700">{c2}</text>
    <text x="28" y="132" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="20">{c2a}</text>
    <text x="28" y="164" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="20">{c2b}</text>
  </g>
  <path d="M792 140 H828" stroke="#d62828" stroke-width="3"/>
  <path d="M818 130 L832 140 L818 150" fill="none" stroke="#d62828" stroke-width="3"/>
  <g transform="translate(840 40)">
    <rect width="320" height="200" rx="20" fill="#fffaf3" stroke="#e4cdb0"/>
    <text x="28" y="44" fill="#d62828" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace" font-size="18">03</text>
    <text x="28" y="92" fill="#2b2118" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="28" font-weight="700">{c3}</text>
    <text x="28" y="132" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="20">{c3a}</text>
    <text x="28" y="164" fill="#7a654f" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif" font-size="20">{c3b}</text>
  </g>
</svg>
"""


def write(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8", newline="\n")


# All Chinese via unicode escapes so this file stays ASCII-safe.
C = {
    "title": "\u67dc\u53f0\u52a9\u624b\u6f14\u793a",
    "desc": "\u586b\u5165 OpenAI \u517c\u5bb9 API Key \u5373\u53ef\u63d0\u95ee\u3002\u5bfc\u822a\u5176\u5b83\u680f\u662f\u5360\u4f4d\uff0c\u6ca1\u6709\u771f\u5b9e\u6536\u94f6\u8d26\u672c\u3002",
    "eyebrow": "\u67dc\u53f0\u6f14\u793a \u00b7 \u65e0\u9700\u767b\u5f55",
    "name": "\u67dc\u53f0\u52a9\u624b\u6f14\u793a",
    "line1": "\u586b\u5165 API Key\uff0c\u5c31\u80fd\u95ee\u8425\u4e1a\u4e0e\u5ba2\u6d41\u3002",
    "line2": "\u5176\u5b83\u6536\u94f6\u53f0\u680f\u4f4d\u662f\u5360\u4f4d\u3002\u786e\u8ba4\u4e0d\u4f1a\u6539\u8d26\u3002",
    "chip1": "\u65e0\u9700\u767b\u5f55",
    "tab_orders": "\u8ba2\u5355",
    "tab_agent": "\u52a9\u624b",
    "tab_settings": "\u8bbe\u7f6e",
    "chip_sales": "\u4eca\u5929\u8425\u4e1a\u989d\u662f\u591a\u5c11",
    "chip_hours": "\u5f00\u53f0\u65f6\u6bb5\u4e3b\u8981\u662f\u4ec0\u4e48",
    "demo_label": "\u6f14\u793a\u6570\u636e",
    "demo_amount": "\u4eca\u65e5\u8425\u4e1a\u989d 1280.00 \u5143",
    "demo_note": "\u4e3b\u8981\u4ee5\u626b\u7801\u652f\u4ed8 \u00b7 \u5ea7\u4f4d\u56fe\u672a\u63a5\u5165",
}

write("hero.svg", HERO.format(**C))

write(
    "section-use.svg",
    SECTION.format(
        title="\u5f00\u59cb\u4f7f\u7528",
        desc="\u4e24\u53f0\u7ec8\u7aef\u542f\u52a8\u540e\uff0c\u5230\u8bbe\u7f6e\u7c98\u8d34\u5bc6\u94a5\uff0c\u518d\u56de\u52a9\u624b\u63d0\u95ee\u3002",
        sub="Python \u8d77\u540e\u7aef\uff0cNode \u8d77\u524d\u7aef\uff0c\u8bbe\u7f6e\u91cc\u586b Key\u3002",
    ),
)
write(
    "section-scope.svg",
    SECTION.format(
        title="\u6f14\u793a\u8303\u56f4",
        desc="\u52a9\u624b\u80fd\u67e5\u6f14\u793a\u6570\u5b57\uff1b\u5ea7\u4f4d\u3001\u5f00\u53f0\u3001\u7ed3\u7b97\u3001\u6539\u4ef7\u53ea\u51fa\u5360\u4f4d\u6216\u786e\u8ba4\u5361\u3002",
        sub="\u6570\u5b57\u548c\u56fe\u662f\u5047\u6570\u636e\u3002\u5199\u5165\u52a8\u4f5c\u4e0d\u4f1a\u6539\u4efb\u4f55\u8d26\u3002",
    ),
)
write(
    "section-wire.svg",
    SECTION.format(
        title="\u63a5\u5230\u67dc\u53f0",
        desc="\u5b9e\u73b0 PosPort\uff0c\u66ff\u6362 DemoPosAdapter\u3002\u672c\u4ed3\u4e0d\u542b\u771f\u5b9e\u8d26\u672c\u3002",
        sub="\u5b9e\u73b0 PosPort\uff0c\u6362\u6389\u6f14\u793a\u9002\u914d\u5668\u3002\u672c\u4ed3\u4e0d\u542b\u8d26\u672c\u3002",
    ),
)
write(
    "workflow.svg",
    WORKFLOW.format(
        title="\u7b2c\u4e00\u6b21\u6210\u529f\u8def\u5f84",
        desc="\u8bbe\u7f6e\u91cc\u7c98\u8d34\u5bc6\u94a5\uff0c\u56de\u5230\u52a9\u624b\u63d0\u95ee\uff0c\u5f97\u5230\u6f14\u793a\u6570\u5b57\u4e0e\u56fe\uff0c\u6216\u672a\u63a5\u5165\u786e\u8ba4\u5361\u3002",
        c1="\u8bbe\u7f6e",
        c1a="\u7c98\u8d34 API Key",
        c1b="\u6d4b\u8bd5\u540e\u4fdd\u5b58",
        c2="\u52a9\u624b",
        c2a="\u9ed8\u8ba4\u505c\u5728\u8fd9\u4e00\u680f",
        c2b="\u53ef\u4e00\u53e5\u8fde\u95ee\u4e09\u4ef6\u4e8b",
        c3="\u56de\u590d",
        c3a="\u6f14\u793a\u6570\u5b57\u4e0e\u56fe",
        c3b="\u6216\u672a\u63a5\u5165\u786e\u8ba4\u5361",
    ),
)

print("wrote", [p.name for p in sorted(OUT.glob("*.svg"))])
