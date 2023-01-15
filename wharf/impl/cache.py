from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING, Any, Dict, Optional

import discord_typings as dt

from ..impl import Guild, Member, Role, TextChannel, User

if TYPE_CHECKING:
    from ..http import HTTPClient

_log = getLogger(__name__)


class Cache:
    def __init__(self, http: HTTPClient):
        self.http = http
        self.users: dict[dt.Snowflake, User] = {}

        # Guild Cache
        self.guilds: Dict[int, Guild] = {}
        self.members: Dict[int, Dict[int, Member]] = {}
        self.channels: Dict[int, Dict[int, TextChannel]] = {}
        self.roles: Dict[int, Dict[int, Role]] = {}

        self.cache_done: bool = False

    def remove_guild(self, guild_id: int) -> None:
        guild = self.get_guild(guild_id)
        assert guild is not None

        guild._members = {}
        guild._channels = {}
        self.channels.pop(guild_id)
        self.members.pop(guild_id)
        self.guilds.pop(guild_id)
        self.roles.pop(guild_id)

    def remove_channel(self, guild_id: int, channel_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        assert guild is not None

        guild._remove_channel(channel_id)
        self.channels[guild_id].pop(channel_id)

        return guild

    def remove_member(self, guild_id: int, member_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        assert guild is not None

        guild._remove_member(member_id)
        self.members[guild_id].pop(member_id)

        return guild

    def remove_role(self, guild_id: int, role_id: int):
        if guild_id not in self.roles or role_id not in self.roles.values():
            raise ValueError("Role or Guild does not appear there!")

        guild = self.get_guild(guild_id)
        assert guild is not None

        guild._remove_role(role_id)
        self.roles[guild_id].pop(role_id)

        return guild

    def get_user(self, user_id: dt.Snowflake):
        return self.users.get(user_id)

    def add_user(self, payload: Dict[str, Any]):
        user = self.users.get(payload["id"])

        if user:
            return user

        user = User(payload, self)
        self.users[user.id] = user
        return user

    def get_guild(self, guild_id: int):
        return self.guilds.get(guild_id)

    def add_guild(self, payload: Dict[str, Any]):
        guild = self.guilds.get(int(payload["id"]))
        if guild:
            return guild

        guild = Guild(payload, self)

        id = int(guild.id)
        self.guilds[id] = guild

        return guild

    def get_channel(self, guild_id: int, channel_id: int) -> Optional[TextChannel]:
        return self.channels[guild_id].get(channel_id)

    def add_channel(self, guild_id: int, payload: Dict[str, Any]) -> TextChannel:
        if guild_id not in self.channels:
            self.channels[guild_id] = {}

        channel = self.channels[guild_id].get(payload["id"])

        if channel:
            return channel

        channel = TextChannel(payload, self)
        guild = self.get_guild(guild_id)
        assert guild is not None

        self.channels[guild_id][channel.id] = channel
        guild._add_channel(channel)
        return channel

    def add_role(self, guild_id: int, payload: Dict[str, Any]):
        if guild_id not in self.roles:
            self.roles[guild_id] = {}

        role = self.roles[guild_id].get(payload["id"])

        if role:
            return role

        role = Role(payload, self)
        guild = self.get_guild(guild_id)
        assert guild is not None

        self.roles[guild_id][role.id] = role
        guild._add_role(role)

        return role

    def get_role(self, guild_id: int, role_id: int) -> Optional[Role]:
        return self.roles[guild_id].get(role_id)

    def get_member(self, guild_id: int, member_id: int) -> Optional[Member]:
        return self.members[guild_id].get(member_id)

    def add_member(self, guild_id: int, payload: Dict[str, Any]):
        if guild_id not in self.members:
            self.members[guild_id] = {}

        member = self.members[guild_id].get(payload["user"]["id"])

        if member:
            return member

        member = Member(payload, self)
        guild = self.get_guild(guild_id)
        assert guild is not None

        self.members[guild_id][member.id] = member
        guild._add_member(member)
        return member

    async def populate_server(self, guild_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        assert guild is not None

        members = await self.http.get_guild_members(guild_id)
        channels = await self.http.get_guild_channels(guild_id)
        roles = await self.http.get_guild_roles(guild_id)

        for channel in channels:
            self.add_channel(guild_id, channel)  # type: ignore
        for role in roles:
            self.add_role(guild_id, role)  # type: ignore

        for member in members:
            self.add_user(member["user"])  # type: ignore
            self.add_member(guild_id, member)  # type: ignore

        return guild

    async def _handle_guild_caching(self, data: Dict[str, Any]):
        _log.info("Adding guild %s to cache!", data["id"])
        self.add_guild(data)
        _log.info("Populating guild %s's cache", data["id"])
        await self.populate_server(int(data["id"]))
