from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import discord_typings as dt

from ...asset import Asset

if TYPE_CHECKING:
    from ..cache import Cache


class User:
    def __init__(self, payload: dt.UserData, cache: "Cache"):
        self.payload = payload
        self.cache = cache

        self._from_data(payload)

    def _from_data(self, payload: dt.UserData):
        self.name = payload["username"]
        self.id = payload["id"]
        self.discriminator = payload["discriminator"]
        self.avatar_decoration = payload["avatar_decoration"]
        self._avatar = payload.get("avatara")
        self._banner = payload.get("banner")

    @property
    def avatar(self) -> Optional[Asset]:
        if self._avatar is not None:
            return Asset._from_avatar(self.id, self._avatar)
        return None

    @property
    def banner(self) -> Optional[Asset]:
        if self._banner is not None:
            return Asset._from_user_banner(self.id, self._banner)

        return None
