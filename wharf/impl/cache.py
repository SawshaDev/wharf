from __future__ import annotations

from asyncio import gather
from logging import getLogger
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import discord_typings as dt

from ..impl import Channel, Guild, Member

if TYPE_CHECKING:
    from ..http import HTTPClient

_log = getLogger(__name__)


class Cache:
    """
    Handles all sorts of cache!

    """

    def __init__(self, http: HTTPClient):
        self.http = http
        self.guilds: Dict[dt.Snowflake, Guild] = {}
        self.members: Dict[dt.Snowflake, Dict[str, Member]] = {}
        self.channels: Dict[dt.Snowflake, Dict[str, Channel]] = {}

    def get_guild(self, guild_id: dt.Snowflake):
        return self.guilds[guild_id]

    def add_guild(self, payload: dt.GuildData):
        guild = self.guilds.get(payload["id"])
        if guild:
            return guild

        guild = Guild(payload, self)

        self.guilds[guild.id] = guild

        return guild

    def get_channel(self, channel_id: int) -> Channel:
        return self.channels[channel_id]

    def add_channel(self, guild_id: int, payload: dt.ChannelData):
        if guild_id not in self.channels:
            self.channels[guild_id] = {}

        channel = self.channels[guild_id].get(payload["id"])

        if channel:
            return channel

        channel = Channel(payload, self)
        guild = self.get_guild(guild_id)
        self.channels[guild_id][channel.id] = channel
        guild._add_channel(channel)
        return channel

    def get_member(self, guild_id: str, member_id: str) -> Member:
        return self.members[guild_id][member_id]

    def add_member(self, guild_id: dt.Snowflake, payload: dt.GuildMemberData):
        """
        Adds members to cache!
        """

        if guild_id not in self.members:
            self.members[guild_id] = {}

        member = self.members[guild_id].get(payload["user"]["id"])

        if member:
            return member

        member = Member(payload, self)
        guild = self.get_guild(guild_id)
        self.members[guild_id][member.id] = member
        guild._add_member(member)
        return member

    async def populate_server(self, guild_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        members = await self.http.get_guild_members(guild_id)
        channels = await self.http.get_guild_channels(guild_id)

        for channel in channels:
            self.add_channel(guild_id, channel)

        for member in members:
            self.add_member(guild_id, member)

        return guild

    async def handle_guild_caching(self, data: dt.GuildData):
        _log.info("Adding guild %s to cache!", data["id"])
        self.add_guild(data)
        _log.info("Populating guild %s's cache", data["id"])
        await self.populate_server(data["id"])
