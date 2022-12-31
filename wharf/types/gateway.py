from __future__ import annotations

from typing import TypedDict, Any, Dict


class GatewayData(TypedDict):
    t: str
    s: int
    op: int
    d: Dict[str, Any]