import asyncio
from typing import List, Optional

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


class Bot:
    def __init__(
        self, 
        *,
        token: str, 
        intents: Intents, 
        cache: Optional[Cache] = Cache
    ):
        self.intents = intents
        self.token = token
        self._slash_commands = []
        self.http = HTTPClient()
        self.cache: Cache = cache(self.http)
        
        self.dispatcher = Dispatcher(self.cache)

        # ws gets filled in later on
        self.ws: Gateway = None  # type: ignore

    async def pre_ready(self):
        """
        Usually supposed to be overwritten lol
        """
        pass

    async def login(self):
        self.http.login(self.token, self.intents.value)

        await self.pre_ready()

    async def connect(self):
        self.ws = Gateway(self.dispatcher, self.cache)
        await self.ws.connect()

    def listen(self, name: str):
        def inner(func):
            if name not in self.dispatcher.events:
                self.dispatcher.subscribe(name, func)
            else:
                self.dispatcher.add_callback(name, func)

        return inner

    def subscribe(self, event: str, func: CoroFunc):
        self.dispatcher.subscribe(event, func)

    async def change_presence(self, *, status: Status, activity: Activity = None):
        await self.ws._change_precense(status=status.value, activity=activity)

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
            asyncio.run(self.close())

    async def close(self):

        if self.ws is not None:
            await self.ws.close()

        await self.http.close()
