from __future__ import annotations

from typing import Any, Dict, Optional

from .enums import ActivityType


class Activity:
    __slots__ = ("type", "name", "url")

    def __init__(self, **kwargs: Any):
        self.name = kwargs.pop("name")
        self.url: Optional[str] = kwargs.pop("url", None)

        activity_type = kwargs.pop("type", -1)
        self.type: ActivityType = activity_type

    def to_dict(self) -> Dict[str, Any]:
        payload = {"name": self.name, "type": int(self.type), "url": self.url}

        return payload
