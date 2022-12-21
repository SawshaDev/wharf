from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import discord_typings as dt

from ...asset import Asset

from .role import Role

if TYPE_CHECKING:
    from ..cache import Cache


class Member:
    def __init__(self, payload: dt.GuildMemberData, cache: "Cache"):
        self.cache = cache
        self._payload = payload
        self._from_data(payload)

        self._roles = []
        self._get_roles()

    def __str__(self) -> str:
        return f"{self.name}#{self.discriminator}"

    def _from_data(self, payload: dt.GuildMemberData):
        self.guild_avatar = payload.get("avatar")
        self.joined_at = payload["joined_at"]
        self.discriminator = payload["user"]["discriminator"]
        self.id = int(payload["user"]["id"])
        self.name = payload["user"]["username"]
        self._avatar = payload["user"].get("avatar")

    def _get_roles(self):
        if self._payload.get("roles"):
            for role in self._payload.get("roles"):
                self._roles.append(Role(role, self.cache))

    @property
    def avatar(self) -> Optional[Asset]:
        if self._avatar is not None:
            return Asset._from_avatar(self.id, self._avatar, self.cache)
        return None
