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

    async def fetch_user(self, user_id: int):
        """
        Fetches and puts in cache a user through an user id

        Parameters
        -----------
        user_id: :class:`int`
            The id of the user you want fetched and then cached.

        Returns
        -----------
        :class:`User`
            The cached user object
        """

        user_data = await self.http.get_user(user_id)

        user = User(user_data, self)

        self.users[user_id] = user

        return user

    def remove_guild(self, guild_id: int) -> None:
        guild = self.guilds[guild_id]

        guild._members = {}
        guild._channels = {}
        self.channels.pop(guild_id)
        self.members.pop(guild_id)
        self.guilds.pop(guild_id)
        self.roles.pop(guild_id)

    def remove_channel(self, guild_id: int, channel_id: int) -> Guild:
        guild = self.guilds[guild_id]

        guild._remove_channel(channel_id)
        self.channels[guild_id].pop(channel_id)

        _log.info("Removed channel %s from cache", channel_id)

        return guild

    def remove_member(self, guild_id: int, member_id: int) -> Member:
        guild = self.guilds[guild_id]

        guild._remove_member(member_id)
        mem = self.members[guild_id].pop(member_id)

        return mem

    def remove_role(self, guild_id: int, role_id: int):
        if guild_id not in self.roles or role_id not in self.roles.values():
            raise ValueError("Role or Guild does not appear there!")

        guild = self.guilds[guild_id]

        guild._remove_role(role_id)
        self.roles[guild_id].pop(role_id)

        return guild

    def get_user(self, user_id: dt.Snowflake):
        return self.users.get(user_id)

    def add_user(self, payload: Any):
        user = self.users.get(payload["id"])

        if user:
            return user

        user = User(payload, self)
        self.users[user.id] = user
        return user

    def get_guild(self, guild_id: int):
        return self.guilds.get(guild_id)

    def add_guild(self, payload: Any):
        guild = self.guilds.get(int(payload["id"]))
        if guild:
            return guild

        guild = Guild(payload, self)

        id = int(guild.id)
        self.guilds[id] = guild

        return guild

    def get_channel(self, guild_id: int, channel_id: int) -> Optional[TextChannel]:
        return self.channels[guild_id].get(channel_id)

    def add_channel(self, guild_id: int, payload: Any) -> TextChannel:
        if guild_id not in self.channels:
            self.channels[guild_id] = {}

        channel = self.channels[guild_id].get(payload["id"])

        if channel:
            return channel

        channel = TextChannel(payload, self)
        guild = self.guilds[guild_id]

        self.channels[guild_id][channel.id] = channel
        guild._add_channel(channel)
        _log.info("added channel %s from cache", channel.id)

        return channel

    def add_role(self, guild_id: int, payload: Any):
        if guild_id not in self.roles:
            self.roles[guild_id] = {}

        role = self.roles[guild_id].get(payload["id"])

        if role:
            return role

        role = Role(payload, self)
        guild = self.guilds[guild_id]

        self.roles[guild_id][role.id] = role
        guild._add_role(role)

        return role

    def get_role(self, guild_id: int, role_id: int) -> Optional[Role]:
        return self.roles[guild_id].get(role_id)

    def get_member(self, guild_id: int, member_id: int) -> Optional[Member]:
        return self.members[guild_id].get(member_id)

    def add_member(self, guild_id: int, payload: Any):
        if guild_id not in self.members:
            self.members[guild_id] = {}

        member = self.members[guild_id].get(payload["user"]["id"])

        if member:
            return member

        guild = self.guilds[guild_id]
        member = Member(payload, guild, self)

        self.members[guild_id][member.id] = member
        guild._add_member(member)

        return member

    async def populate_server(self, guild_id: int) -> Guild:
        guild = self.guilds[guild_id]

        members = await self.http.get_guild_members(guild_id)
        channels = await self.http.get_guild_channels(guild_id)
        roles = await self.http.get_guild_roles(guild_id)

        for channel in channels:
            self.add_channel(guild_id, channel)
        for role in roles:
            self.add_role(guild_id, role)

        for member in members:
            self.add_user(member['user'])  # type: ignore # Not sure how to fix `"Literal['user']" is incompatible with "slice"` but ill deal with that later 📌
            self.add_member(guild_id, member)

        return guild

    async def _handle_guild_caching(self, data: Dict[str, Any]):
        _log.info("Adding guild %s to cache!", data["id"])
        self.add_guild(data)
        _log.info("Populating guild %s's cache", data["id"])
        await self.populate_server(int(data["id"]))
