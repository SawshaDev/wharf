from __future__ import annotations

import asyncio
import json
import logging
import random
import time
import zlib
from sys import platform as _os
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from aiohttp import ClientWebSocketResponse, WSMsgType

from .activities import Activity
from .dispatcher import Dispatcher
from .errors import WebsocketClosed

if TYPE_CHECKING:
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
        ws: ClientWebSocketResponse
        _resume_url: str
        _last_sequence: int

    def __init__(self, dispatcher: Dispatcher, cache: Cache):
        self.cache = cache
        self.token = self.cache.http._token
        self.intents = self.cache.http._intents
        self.api_version = 10
        self.gateway_url: str = f"wss://gateway.discord.gg/?v={self.api_version}&encoding=json&compress=zlib-stream"
        self._first_heartbeat = True
        self.dispatcher = dispatcher
        self._decompresser = zlib.decompressobj()
        self.loop = None
        self.ws: Optional[ClientWebSocketResponse] = None
        self._last_sequence: Optional[int] = None

    def _decompress_msg(self, msg: Union[bytes, str]):
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
                "seq": self._last_sequence or 0,
                "session_id": self.session_id,
            },
        }

    @property
    def ping_payload(self):
        payload = {"op": OPCodes.heartbeat}

        if self._last_sequence is None:
            payload["d"] = {}
        else:
            payload["d"] = self._last_sequence

        return payload

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

    async def _change_presence(self, *, status: str, activity: Activity = None):
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

    async def connect(
        self, *, url: Optional[str] = None, reconnect: Optional[bool] = False
    ):
        self.ws = await self.cache.http._session.ws_connect(url or self.gateway_url)

        _log.info("Connected to gateway")

        while not self.is_closed:
            msg = await self.ws.receive()

            if msg.type in (WSMsgType.BINARY, WSMsgType.TEXT):
                data: Union[Any, str] = None
                if msg.type == WSMsgType.BINARY:
                    data = self._decompress_msg(msg.data)
                elif msg.type == WSMsgType.TEXT:
                    data = msg.data

                data: Dict[Any, str] = json.loads(data)

            if data.get("s"):
                self._last_sequence = data.get("s", 0)

            _log.info(data["op"])

            if data["op"] == OPCodes.hello:
                self.heartbeat_interval = data["d"]["heartbeat_interval"]

                asyncio.create_task(self.keep_heartbeat())

                if reconnect:
                    await self.send(self.resume_payload)
                else:
                    await self.send(self.identify_payload)

                self._last_send = time.perf_counter()

            elif data["op"] == OPCodes.heartbeat:
                await self.send(self.ping_payload)
                self._last_send = time.perf_counter()

            elif data["op"] == OPCodes.dispatch:
                event_data = data["d"]

                _log.info(data["t"])

                if data["t"] == "READY":
                    self.session_id = event_data["session_id"]
                    self._resume_url = event_data["resume_gateway_url"]

                # As messy as this all is, this probably is best here.
                if data["t"] == "GUILD_CREATE":
                    asyncio.create_task(self.cache.handle_guild_caching(event_data))

                elif data["t"] == "GUILD_MEMBER_ADD":
                    await self.cache.add_member(int(event_data["guild_id"]), event_data)

                elif data["t"] == "GUILD_DELETE":
                    self.cache.remove_guild(int(event_data["id"]))

                elif data["t"] == "GUILD_MEMBER_REMOVE":
                    self.cache.remove_member(
                        int(event_data["guild_id"]), int(event_data["user"]["id"])
                    )

                elif data["t"] == "CHANNEL_DELETE":
                    self.cache.remove_channel(
                        int(event_data["guild_id"]), int(event_data["id"])
                    )

                else:
                    if data["t"].lower() not in self.dispatcher.events.keys():
                        continue

                    self.dispatcher.dispatch(data["t"].lower(), event_data)

            elif data["op"] == OPCodes.heartbeat_ack:
                self._last_heartbeat_ack = time.perf_counter()
                self.latency = self._last_heartbeat_ack - self._last_send

            elif data["op"] == OPCodes.resume:
                await self.close(code=4000, resume=True)

            elif data["op"] == OPCodes.reconnect:
                _log.info("Reconnected! :)")
                await self.close(code=4000, resume=True)

            elif data["op"] == OPCodes.invalid_session:
                # If we're getting an invalid session, do NOT try to reconnect
                # We get invalid session for various reasons (https://discord.com/developers/docs/topics/gateway-events#invalid-session), most of the time these are fatal.
                _log.info("Invalid session! We will not be reconnecting.")
                await self.close(code=4001, resume=False)
                break

            elif msg.type == WSMsgType.CLOSE:
                raise WebsocketClosed(msg.data, msg.extra)

    async def close(self, *, code: int = 1000, resume: bool = True):
        if not self.ws:
            return

        if not self.is_closed:
            await self.ws.close(code=code)

            if resume:
                await self.connect(url=self._resume_url, reconnect=True)

    @property
    def is_closed(self):
        return self.ws.closed if self.ws else False
