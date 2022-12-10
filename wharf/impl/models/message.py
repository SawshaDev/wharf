from typing import TYPE_CHECKING

import discord_typings as dt

from .user import User

if TYPE_CHECKING:
    from ..cache import Cache


class Message:
    def __init__(self, data: dt.MessageCreateData, cache: "Cache"):
        self._from_data(data)
        self.cache = cache

    def _from_data(self, message: dt.MessageData):
        self.content = message.get("content")
        self.author = User(message["author"])
        self.channel_id = message["channel_id"]

    async def send(self, content: str):
        msg = await self.cache.http.send_message(self.channel_id, content=content)
        return Message(msg, self.cache)
