from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import discord_typings as dt

from ...asset import Asset
from .role import Role

if TYPE_CHECKING:
    from ..cache import Cache


class Member:
    def __init__(self, payload: Dict[str, Any], cache: "Cache"):
        self.cache = cache
        self._payload = payload
        self._from_data(payload)

        self._roles = []

    def __str__(self) -> str:
        return f"{self.name}#{self.discriminator}"

    def _from_data(self, payload: Dict[str, Any]):
        self.guild_avatar = payload.get("avatar")
        self.joined_at = payload["joined_at"]
        self.discriminator = payload["user"]["discriminator"]
        self.id = int(payload["user"]["id"])
        self.name = payload["user"]["username"]
        self._avatar = payload["user"].get("avatar")
        self.permissions = payload["permissions"]

    @property
    def avatar(self) -> Optional[Asset]:
        if self._avatar is not None:
            return Asset._from_avatar(self.id, self._avatar, self.cache)
        return None
