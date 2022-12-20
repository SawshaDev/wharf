from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

import discord_typings as dt

from ...asset import Asset
from .channel import TextChannel
from .member import Member
from .role import Role

if TYPE_CHECKING:
    from ..cache import Cache


class Guild:
    def __init__(self, data: dt.GuildData, cache: "Cache"):
        self._from_data(data)
        self.cache = cache
        self._members: Dict[int, Member] = {}
        self._channels: Dict[int, TextChannel] = {}

    def _from_data(self, guild: dt.GuildData):
        self.name = guild.get("name")
        self.id: int = guild.get("id")
        self.icon_hash = guild.get("icon")
        self.banner_hash = guild.get("banner")

    async def fetch_member(self, member_id: int):
        return Member(await self.cache.http.get_member(member_id, self.id))

    def get_member(self, member_id: int):
        return self.cache.get_member(self.id, member_id)

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

    def _add_member(self, member: Member):
        """
        This function is meant to be used internally with the websocket to add to cache.
        i dont honestly recommend using this at any point.
        shouldn't even be necessary to use it lol
        """

        self._members[member.id] = member

    def _add_channel(self, channel: TextChannel):
        """
        This function is meant to be used internally with the websocket to add to cache.
        i dont honestly recommend using this at any point either.
        shouldn't even be necessary to use it lol
        """

        self._channels[channel.id] = channel

    def _remove_member(self, member_id: int):
        self._members.pop(member_id)

    def _remove_channel(self, channel_id: int):
        self._channels.pop(channel_id)

    @property
    def members(self) -> List[Member]:
        """
        A list of all the members this server has.
        """
        return list(self._members.values())

    @property
    def channels(self) -> List[TextChannel]:
        """
        A list of all the channels this server has.
        """
        return list(self._channels.values())

    @property
    def icon(self) -> Optional[Asset]:
        if self.icon_hash is None:
            return None
        return Asset._from_guild_icon(self.cache, self.id, self.icon_hash)

    @property
    def banner(self) -> Optional[Asset]:
        if self.banner_hash is None:
            return None
        return Asset._from_guild_image(
            self.cache, self.id, self.banner_hash, path="banners"
        )
