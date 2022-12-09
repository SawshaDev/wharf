import discord_typings as dt

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...client import Client

class Role:
    def __init__(self, payload: dt.RoleData, bot: 'Client'):
        self._from_data(payload)
        self.bot = bot

    def _from_data(self, payload: dt.RoleData):
        self.name = payload['name']
        self.id = payload['id']
        self.color = payload['color']
        self.hoist = payload['hoist']

