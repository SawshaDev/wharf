from typing import TYPE_CHECKING, Dict, List

import discord_typings as dt

from .member import Member

from .role import Role

if TYPE_CHECKING:
    from ..cache import Cache


class Guild:
    def __init__(self, data: dt.GuildData, cache: "Cache"):
        self._from_data(data)
        self.cache = cache
        self._members: Dict[int, Member] = {}


    def _from_data(self, guild: dt.GuildData):
        self.name = guild.get("name")
        self.id = guild.get("id")
        self.icon_hash = guild.get("icon")

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

    @property
    def members(self) -> List[Member]:
        """
        A list of all the members this server has.
        """
        return list(self._members.values())