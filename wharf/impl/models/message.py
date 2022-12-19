from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Dict

import discord_typings as dt

from .user import User

if TYPE_CHECKING:
    from ..cache import Cache


class Message:
    def __init__(self, data: Dict[str, str], cache: "Cache"):
        self._from_data(data)
        self.cache = cache

    def _from_data(self, message: Dict[str, str]):
        self._content = message.get("content")
        self._author = message["author"]
        self._channel_id = message["channel_id"]

    @property
    def channel_id(self) -> int:
        return int(self._channel_id)

        

    async def send(self, content: str):
        msg = await self.cache.http.send_message(self.channel_id, content=content)
        return Message(msg, self.cache)
