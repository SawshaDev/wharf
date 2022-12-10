from typing import TYPE_CHECKING

import discord_typings as dt

from .member import Member

from .role import Role

if TYPE_CHECKING:
    from ..cache import Cache


class Guild:
    def __init__(self, data: dt.GuildData, cache: "Cache"):
        self._from_data(data)
        self.cache = cache

    def _from_data(self, guild: dt.GuildData):
        self.name = guild.get("name")
        self.id = guild.get("id")
        self.icon_hash = guild.get("icon")

    async def fetch_member(self, user: int):
        return Member(await self.cache.http.get_member(user, self.id))

    async def ban(
        self,
        user_id: int,
        *,
        reason: str,
    ):
        await self.cache.http.ban(self.id, user_id, reason)

    async def create_role(self, name: str, *, reason: str = None) -> Role:
        payload = await self.cache.http.create_role(self.id, name=name, reason=reason)
        return Role(payload, self.cache)
