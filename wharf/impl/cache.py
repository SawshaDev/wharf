from __future__ import annotations

from asyncio import gather

from typing import TYPE_CHECKING, Any, List, Dict, Optional

import discord_typings as dt

from ..impl import Guild
from ..impl import Member

if TYPE_CHECKING:
    from ..http import HTTPClient

class Cache:
    """
    Handles all sorts of cache!
    
    """

    def __init__(self, http: HTTPClient):
        self.http = http
        self.guilds: Dict[dt.Snowflake, Guild] = {}
        self.members: Dict[dt.Snowflake, Dict[str, Member]] = {}

    def get_guild(self, guild_id: dt.Snowflake):
        return self.guilds[guild_id]

    def add_guild(self, payload: dt.GuildData):
        guild = self.guilds.get(payload['id'])
        if guild:
            return guild

        guild = Guild(payload, self)

        self.guilds[guild.id] = guild

        return guild

    def get_member(self, guild_id: str, member_id: str) -> Member:
    
        return self.members[guild_id][member_id]

    def add_member(self, guild_id: dt.Snowflake, payload: dt.GuildMemberData):
        """
        Adds members to cache!
        """

        if guild_id not in self.members:
            self.members[guild_id] = {}
        
        member = self.members[guild_id].get(payload['user']['id'])
        
        if member: 
            return member

        member = Member(payload, self)
        guild = self.get_guild(guild_id)
        self.members[guild_id][member.id] = member
        guild._add_member(member)
        return member

    async def populate_server(self, guild_id: int) -> Guild:
        guild = self.get_guild(guild_id)
        data = await self.http.get_guild_members(guild_id)

        for member in data:
            self.add_member(guild_id, member)
        return guild

    async def populate_all_servers(self): 
        for guild_id in self.guilds:
            await self.populate_server(guild_id)


    async def handle_guild_caching(self, data: dt.GuildData):
        self.add_guild(data)
        await self.populate_all_servers()





        