from __future__ import annotations

import asyncio
import importlib
import logging
import sys
from typing import Dict, List, Optional, Protocol, Union, cast

from .activities import Activity
from .dispatcher import CoroFunc, Dispatcher
from .enums import Status
from .errors import GatewayReconnect
from .file import File
from .gateway import Gateway
from .http import HTTPClient
from .impl import Guild, InteractionCommand, User, check_channel_type
from .impl.cache import Cache
from .intents import Intents
from .plugin import Plugin


_log = logging.getLogger(__name__)

class ExtProtocol(Protocol):
    def load(self, bot: Bot):
        ...

    def remove(self, bot: Bot):
        ...


class Bot:
    def __init__(
        self, *, token: str, intents: Intents, cache: Cache = Cache, purge_old_slash: bool = False  # type: ignore
    ):
        self.intents = intents
        self.token = token
        self._slash_commands = []
        self.http = HTTPClient()
        self.cache: Cache = cache(self.http)  # type: ignore
        self.dispatcher = Dispatcher(self.cache)
        self.purge_slash = purge_old_slash

        # ws gets filled in later on
        self.gateway: Gateway = None  # type: ignore

        self.extensions: List[ExtProtocol] = []

        self._plugins: Dict[str, Plugin] = {}

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        *args,
    ) -> None:
        if not self.gateway.is_closed:
            await self.close()


    async def pre_ready(self):
        """
        Usually supposed to be overwritten lol
        """
        pass

    async def login(self):
        self.http.login(self.token, self.intents.value)

        await self.pre_ready()

    async def connect(self):
        self.gateway = Gateway(self.dispatcher, self.cache)

        gateway_url: Optional[str] = None
        self.running = True

        while self.running:
            try:
                await self.gateway.connect(gateway_url)
            except GatewayReconnect as gr:
                gateway_url = gr.url

    def listen(self, name: str):
        def inner(func):
            if name not in self.dispatcher.events:
                self.dispatcher.subscribe(name, func)
            else:
                self.dispatcher.add_callback(name, func)

        return inner

    def subscribe(self, event: str, func: CoroFunc):
        self.dispatcher.subscribe(event, func)

    def load_extension(self, extension: str):
        if extension in self.extensions:
            raise RuntimeWarning("Extension already loaded!")

        module = importlib.import_module(extension)

        ext = cast(ExtProtocol, module)

        if hasattr(ext, "load") is False:
            raise RuntimeWarning("Extension is missing load function. Please fix this!")

        ext.load(self)

        self.extensions.append(ext)

    def remove_extension(self, extension: str):
        if extension not in self.extensions:
            raise RuntimeWarning("Extension not loaded!")

        module = importlib.import_module(extension)

        ext = cast(ExtProtocol, module)

        if hasattr(ext, "load") is False:
            raise RuntimeWarning("Extension is missing remove function.")

        ext.remove(self)

        self.extensions.remove(ext)

    def fetch_plugin(self, name: str) -> Optional[Plugin]:
        return self._plugins.get(name)

    def add_plugin(self, plugin: Plugin):
        plugin.bot = self

        for event_name, listeners in plugin._listeners.items():
            for listener in listeners:
                self.subscribe(event_name, listener)

        self._plugins[plugin.name] = plugin

    def remove_plugin(self, plugin: Union[str, Plugin]) -> None:
        if isinstance(plugin, str):
            plugin = self.fetch_plugin(plugin)  # type: ignore # Shit crazy?

        if plugin is None:
            return

        self._plugins.pop(plugin.name)  # type: ignore

    async def change_presence(
        self, *, status: Status, activity: Optional[Activity] = None
    ):
        await self.gateway._change_presence(status=status.value, activity=activity)

    async def fetch_user(self, user_id: int):
        return User(await self.http.get_user(user_id), self.cache)

    async def fetch_channel(self, channel_id: int):
        resp = await self.http.get_channel(channel_id)

        return check_channel_type(resp, self.cache)

    async def fetch_guild(self, guild_id: int):

        return Guild(await self.http.get_guild(guild_id), self.cache)

    async def register_app_command(self, command: InteractionCommand):
        await self.http.register_app_commands(command)
        self._slash_commands.append(command._to_json())

    async def start(self):
        await self.login()
        await self.connect()

    def run(self):
        try:
            asyncio.run(self.start())
        except (KeyboardInterrupt, RuntimeError):
            return

    async def close(self):
        if self.purge_slash:
            api_commands = await self.http.get_app_commands()

            for command in api_commands:
                for cached_command in self._slash_commands:
                    _log.info(cached_command)
                    if command["name"] != cached_command["name"]: # type: ignore
                        await self.http.delete_app_command(command)
                        continue
                    else:
                        continue

                    
        for ext in self.extensions:
            ext.remove(self)

        for plugin in self._plugins.values():
            self.remove_plugin(plugin)

        if self.gateway is not None:
            await self.gateway.close(code=1000, resume=False)

        await self.http.close()
