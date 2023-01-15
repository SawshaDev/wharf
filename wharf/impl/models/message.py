from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

import discord_typings as dt

from .guild import Guild
from .user import User

if TYPE_CHECKING:
    from ..cache import Cache
    from .embed import Embed
    from ...file import File
    from .member import Member


class Message:
    def __init__(self, data: Dict[str, str], cache: "Cache"):
        self._data = data
        self._from_data(data)
        self.cache = cache

    def _from_data(self, message: Dict[str, str]):
        self._content = message["content"]
        self._author_id = int(message["author"]["id"])  # type: ignore
        self._channel_id = message["channel_id"]

        if message.get("guild_id") is not None:
            self._guild_id = int(message.get("guild_id"))  # type: ignore

    @property
    def guild(self) -> Optional[Guild]:
        return self.cache.get_guild(self._guild_id)

    @property
    def content(self) -> str:
        return self._content

    @property
    def user(self) -> Optional[User]:
        return self.cache.get_user(self._author_id)

    @property
    def member(self) -> Optional[Member]:
        return self.cache.get_member(self._guild_id, self._author_id)

    @property
    def channel_id(self) -> int:
        return int(self._channel_id)

    async def send(self, content: str, embed: Optional[Embed] = None, file: Optional[File] = None):
        msg = await self.cache.http.send_message(self.channel_id, content=content, embed=embed, file=file)
        return Message(msg, self.cache)
