from __future__ import annotations

from typing import Any, Dict, Optional

from .enums import ActivityType


class Activity:
    __slots__ = ("type", "name", "url")

    def __init__(self, name: str, url: Optional[str] = None, type: ActivityType = ActivityType.unknown):
        self.name = name
        self.url: Optional[str] = url

        activity_type: ActivityType = type
        self.type: ActivityType = activity_type

    def to_dict(self) -> Dict[str, Any]:
        payload = {"name": self.name, "type": int(self.type), "url": self.url}

        return payload
