from __future__ import annotations

from asyncio import gather

from typing import TYPE_CHECKING, Any, List, Dict, Optional

import discord_typings as dt

from ..impl import Guild

if TYPE_CHECKING:
    from ..http import HTTPClient

class Cache:
    """
    Handles all sorts of cache!
    
    """

    def __init__(self, http: HTTPClient):
        self.http = http
        self.guilds: Dict[dt.Snowflake, Guild] = {}

    def get_guild(self, guild_id: dt.Snowflake):
        return self.guilds[guild_id]

    def add_guild(self, payload):
        guild = self.guilds.get(payload['id'])
        if guild:
            return guild

        guild = Guild(payload, self)

        self.guilds[guild.id] = guild

        return guild



        