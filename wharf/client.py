import asyncio
from typing import List

from .activities import Activity
from .dispatcher import Dispatcher
from .enums import Status
from .file import File
from .gateway import Gateway
from .http import HTTPClient
from .impl import Channel, Embed, Guild, InteractionCommand, User
from .impl.cache import Cache
from .intents import Intents


class Client:
    def __init__(self, *, token: str, intents: Intents):
        self.intents = intents
        self.token = token
        self._slash_commands = []
        self.http = HTTPClient(token=self.token, intents=self.intents.value)
        self.cache = Cache(self.http)
        self.dispatcher = Dispatcher(self.cache)
        self.ws = Gateway(self.dispatcher, self.cache, self.http)

    def listen(self, name: str):
        def inner(func):
            if name not in self.dispatcher.events:
                self.dispatcher.subscribe(name, func)
            else:
                self.dispatcher.add_callback(name, func)

        return inner

    def get_user(self, user_id: int):
        return self.cache.get_user(user_id)

    def get_channel(self, *, guild_id: int, channel_id: int):
        return self.cache.get_channel(guild_id, channel_id)

    def get_guild(self, guild_id: int):
        return self.cache.get_guild(guild_id)

    async def change_presence(self, *, status: Status, activity: Activity = None):
        await self.ws._change_precense(status=status.value, activity=activity)

    async def fetch_user(self, user_id: int):
        return User(await self.http.get_user(user_id), self.cache)

    async def fetch_channel(self, channel_id: int):
        return Channel(await self.http.get_channel(channel_id), self.cache)

    async def fetch_guild(self, guild_id: int):

        return Guild(await self.http.get_guild(guild_id), self.cache)

    async def register_app_command(self, command: InteractionCommand):
        await self.http.register_app_commands(command)
        self._slash_commands.append(command._to_json())

    async def start(self):
        await self.ws.connect()

    async def close(self):
        await self.http._session.close()
        await self.ws.ws.close()

        api_commands = await self.http.get_app_commands()

        for command in api_commands:
            for cached_command in self._slash_commands:
                if command["name"] != cached_command["name"]:
                    await self.http.delete_app_command(command)
                    continue
                else:
                    continue

    def run(self):
        try:
            asyncio.run(self.start())
        except (KeyboardInterrupt, RuntimeError):
            asyncio.run(self.close())
