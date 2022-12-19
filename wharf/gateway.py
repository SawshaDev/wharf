from __future__ import annotations

import asyncio
import datetime
import json
import logging
import random
import traceback
import zlib
from sys import platform as _os
from typing import TYPE_CHECKING, Any, List, Optional, Union

from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType

from .activities import Activity
from .dispatcher import Dispatcher
from .errors import GatewayReconnect, WebsocketClosed
from .impl import Guild

if TYPE_CHECKING:
    from .http import HTTPClient
    from .impl.cache import Cache


_log = logging.getLogger(__name__)


class OPCodes:
    dispatch = 0
    heartbeat = 1
    identify = 2
    presence_update = 3
    voice_state_update = 4
    resume = 6
    reconnect = 7
    request_guild_members = 8
    invalid_session = 9
    hello = 10
    heartbeat_ack = 11


class Gateway:
    if TYPE_CHECKING:
        heartbeat_interval: int

    def __init__(self, dispatcher: Dispatcher, cache: Cache):
        self.cache = cache
        self.token = self.cache.http._token
        self.intents = self.cache.http._intents
        self.api_version = 10
        self.gw_url: str = f"wss://gateway.discord.gg/?v={self.api_version}&encoding=json&compress=zlib-stream"
        self._last_sequence: Optional[int] = None
        self._first_heartbeat = True
        self.dispatcher = dispatcher
        self._decompresser = zlib.decompressobj()
        self.loop = None
        self.session: Optional[ClientSession] = None
        self.ws: Optional[ClientWebSocketResponse] = None

    def _decompress_msg(self, msg: bytes):
        ZLIB_SUFFIX = b"\x00\x00\xff\xff"

        out_str: str = ""

        # Message should be compressed
        if len(msg) < 4 or msg[-4:] != ZLIB_SUFFIX:
            return out_str

        buff = self._decompresser.decompress(msg)
        out_str = buff.decode("utf-8")
        return out_str

    @property
    def identify_payload(self):
        return {
            "op": OPCodes.identify,
            "d": {
                "token": self.token,
                "intents": self.intents,
                "properties": {"os": _os, "browser": "wharf", "device": "wharf"},
                "compress": True,
            },
        }

    @property
    def resume_payload(self):
        return {
            "op": OPCodes.resume,
            "d": {
                "token": self.token,
                "seq": self._last_sequence,
                "session_id": self.session_id,
            },
        }

    @property
    def ping_payload(self):
        return {"op": OPCodes.heartbeat, "d": self._last_sequence}

    async def keep_heartbeat(self):
        jitters = self.heartbeat_interval
        if self._first_heartbeat:
            jitters *= random.uniform(1.0, 0.0)
            self._first_heartbeat = False

        await self.ws.send_json(self.ping_payload)
        await asyncio.sleep(jitters / 1000)
        asyncio.create_task(self.keep_heartbeat())

    async def send(self, data: dict):
        await self.ws.send_json(data)
        _log.info("Sent json to the gateway successfully")

    async def _change_precense(self, *, status: str, activity: Activity = None):
        activities = []
        activities.append(activity.to_dict())

        payload = {
            "op": OPCodes.presence_update,
            "d": {
                "status": status,
                "afk": False,
                "since": 0.0,
                "activities": activities,
            },
        }

        await self.ws.send_json(payload)

    async def connect(self, *, url: str = None, reconnect: bool = False):
        if not self.session:
            self.session = ClientSession()

        if not url:
            url = self.gw_url

        self.ws = await self.session.ws_connect(url)

        self.reconnect = reconnect

        while not self.is_closed:
            msg = await self.ws.receive()

            if msg.type in (WSMsgType.BINARY, WSMsgType.TEXT):
                data: Union[Any, str] = None
                if msg.type == WSMsgType.BINARY:
                    data = self._decompress_msg(msg.data)
                elif msg.type == WSMsgType.TEXT:
                    data = msg.data

                data = json.loads(data)

            self._last_sequence = data["s"]

            if data["op"] == OPCodes.hello:
                self.heartbeat_interval = data["d"]["heartbeat_interval"]

                if reconnect:
                    await self.send(self.resume_payload)
                else:
                    await self.send(self.identify_payload)

                asyncio.create_task(self.keep_heartbeat())

            if data["op"] == OPCodes.heartbeat:
                await self.send(self.ping_payload)

            if data["op"] == OPCodes.dispatch:
                event_data = data["d"]

                if data["t"] == "READY":
                    self.session_id = event_data["session_id"]
                    self._resume_url = event_data["resume_gateway_url"]

                if data["t"] == "GUILD_CREATE":
                    await self.cache.handle_guild_caching(event_data)

                if data["t"].lower() not in self.dispatcher.events.keys():
                    continue

                self.dispatcher.dispatch(data["t"].lower(), event_data)

            if data["op"] == OPCodes.heartbeat_ack:
                self._last_heartbeat_ack = datetime.datetime.now()

            if data["op"] == OPCodes.reconnect:
                _log.info("reconnected!!")
                await self.close(resume=True)

            if data["op"] == OPCodes.invalid_session:
                await self.ws.close(code=4001)
                break

            elif msg.type == WSMsgType.CLOSE:
                raise WebsocketClosed(msg.data, msg.extra)

    async def close(self, *, code: int = 1000):
        if not self.ws:
            return

        if not self.is_closed:
            await self.ws.close(code=code)

            if self.reconnect:
                await self.connect(url=self._resume_url, reconnect=True)

    @property
    def is_closed(self):
        return self.ws.closed if self.ws else False
