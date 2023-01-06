from __future__ import annotations

from typing import Any, Dict, TypedDict


class GatewayData(TypedDict):
    t: str
    s: int
    op: int
    d: Dict[str, Any]
