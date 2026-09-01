"""POS adapter contract. Demo ships a stub; a real shop implements this and does not publish it."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class WritePreview:
    tool_name: str
    title: str
    message: str
    compare_rows: list[dict[str, str]] = field(default_factory=list)
    wired: bool = False


class PosPort(Protocol):
    def today(self) -> dict[str, Any]: ...
    def trend(self, days: int = 7) -> dict[str, Any]: ...
    def traffic(self) -> dict[str, Any]: ...
    def seats(self) -> dict[str, Any]: ...
    def preview_write(self, tool_name: str, arguments: dict[str, Any]) -> WritePreview: ...
    def confirm_write(self, preview: WritePreview) -> dict[str, Any]: ...
