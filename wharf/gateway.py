from __future__ import annotations

import asyncio

from aiohttp import ClientWebSocketResponse, WSMsgType

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .impl import Cache
    from .dispatcher import Dispatcher


DEFAULT_API_VERSION = 10


class OPCodes:
    DISPATCH = 0
    HEARTBEAT = 1
    IDENTIFY = 2
    PRESENCE_UPDATE = 3
    VOICE_STATE_UPDATE = 4
    RESUME = 6
    RECONNECT = 7
    REQUEST_GUILD_MEMBERS = 8
    INVALID_SESSION = 9
    HELLO = 10
    HEARTBEAT_ACK = 11


class Gateway: # This Class is in no way supposed to be used by itself. it should ALWAYS be used with `wharf.Bot`. so seriously, dont :sob:
    if TYPE_CHECKING:
        ws: ClientWebSocketResponse
        heartbeat_interval: int
        resume_url: str
        last_sequence: int

    def __init__(self, dispatcher: Dispatcher, cache: Cache, api_version: int = 10):
        self._dispatcher = dispatcher
        self._cache = cache

        # Defining token and intents
        self.token = self._cache.http._token
        self.intents = self._cache.http._intents

        


