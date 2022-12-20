from __future__ import annotations

from asyncio import gather
from logging import getLogger
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import discord_typings as dt

from ..impl import Channel, Guild, Member, User

if TYPE_CHECKING:
    from ..http import HTTPClient

_log = getLogger(__name__)


class Cache:
    def __init__(self, http: HTTPClient):
        self.http = http
        self.guilds: Dict[dt.Snowflake, Guild] = {}
        self.members: Dict[dt.Snowflake, Dict[str, Member]] = {}
        self.channels: Dict[dt.Snowflake, Dict[str, Channel]] = {}
        self.users: dict[dt.Snowflake, User] = {}

    def remove_guild(self, guild_id: int) -> None:
        guild = self.get_guild(guild_id)

        guild._members = {}
        guild._channels = {}
        self.channels.pop(guild_id)
        self.members.pop(guild_id)
        self.guilds.pop(guild_id)

    def remove_channel(self, guild_id: int, channel_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        guild._remove_channel(channel_id)
        self.channels[guild_id].pop(channel_id)

        return guild

    def remove_member(self, guild_id: int, member_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        guild._remove_member(member_id)
        self.members[guild_id].pop(member_id)

        return guild

    def get_user(self, user_id: dt.Snowflake):
        return self.users.get(user_id)

    def add_user(self, payload: dt.UserData):
        user = self.users.get(payload["id"])

        if user:
            return user

        user = User(payload, self)
        self.users[user.id] = user
        return user

    def get_guild(self, guild_id: dt.Snowflake):
        return self.guilds.get(guild_id)

    def add_guild(self, payload: dt.GuildData):
        guild = self.guilds.get(payload["id"])
        if guild:
            return guild

        guild = Guild(payload, self)

        self.guilds[guild.id] = guild

        return guild

    def get_channel(self, guild_id: int, channel_id: int) -> Channel:
        return self.channels.get(guild_id).get(channel_id)

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
        return self.members.get(guild_id).get(member_id)

    def add_member(self, guild_id: dt.Snowflake, payload: dt.GuildMemberData):
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
            self.add_user(member["user"])
            self.add_member(guild_id, member)

        return guild

    async def handle_guild_caching(self, data: dt.GuildData):
        _log.info("Adding guild %s to cache!", data["id"])
        self.add_guild(data)
        _log.info("Populating guild %s's cache", data["id"])
        await self.populate_server(data["id"])
