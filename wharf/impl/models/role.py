from typing import TYPE_CHECKING

import discord_typings as dt

if TYPE_CHECKING:
    from ..cache import Cache


class Role:
    def __init__(self, payload: dt.RoleData, cache: "Cache"):
        self._from_data(payload)
        self.cache = cache

    def _from_data(self, payload: dt.RoleData):
        self._name = payload.get("name")
        self._id = payload["id"]
        self._color = payload["color"]
        self._hoist = payload["hoist"]

    @property
    def name(self) -> str:
        return self._name

    @property
    def id(self) -> int:
        return int(self._id)

    @property
    def color(self) -> int:
        return int(self._color)

    @property
    def hoist(self) -> bool:
        return self._hoist