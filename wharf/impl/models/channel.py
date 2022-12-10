from __future__ import annotations

from typing import TYPE_CHECKING

import discord_typings as dt

if TYPE_CHECKING:
    from ..cache import Cache


class Channel:
    def __init__(self, payload: dt.ChannelData, cache: Cache):
        self.cache = cache
        self._from_data(payload)

    def _from_data(self, payload: dt.ChannelData):
        self.name = payload['name']
        self.id = payload.get("id")
        self.guild_id = payload.get("guild")
