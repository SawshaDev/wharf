from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

import discord_typings as dt

from ...enums import InteractionOptionType, MessageFlags
from ...file import File

if TYPE_CHECKING:
    from ..cache import Cache
    from ..models import Embed


class InteractionOption:
    def __init__(self, payload: dict):
        self._from_data(payload)

    def _from_data(self, payload: dict):
        self._name = payload.get("name")
        self._type = payload.get("type")
        self._value = payload.get("value")

    @property
    def value(self) -> Optional[str]:
        return self._value

    @property
    def name(self) -> Optional[str]:
        return self._name

    def __str__(self):
        return self.value


class Interaction:
    def __init__(self, cache: Cache, payload: dict):
        self.cache = cache
        self.payload = payload
        self.id = payload["id"]
        self.token = payload["token"]
        self.channel_id = payload["channel_id"]
        self.type = payload["type"]
        self.command: Optional[InteractionCommand] = None
        self.options: Optional[List[InteractionOption]] = [] # type: ignore
        
        if self.type == 2:
            self.command = InteractionCommand._from_json(payload)
            self.options: List[InteractionOption] = []
            self._make_options()

        self.guild_id = int(payload.get("guild_id")) # type: ignore
        self._member = payload.get("member") 

        if self._member:
            self._user = self._member["user"]
        else:
            self._user = self.payload["user"]

    @property
    def user(self):
        return self.cache.get_user(self._user["id"])

    @property
    def member(self):
        if self._member:
            return self.cache.get_member(self.guild_id, self._member["id"])
        
        return None

    @property
    def guild(self):
        return self.cache.get_guild(self.guild_id)

    async def reply(
        self,
        content: Optional[str] = None,
        *,
        embed: Optional[Embed] = None,
        flags: Optional[MessageFlags] = None,
        file: Optional[File] = None,
        components: Optional[List[Dict[str, Any]]] = None,
        type: int = 4,
    ) -> None:
        """
        Replies to a discord interaction

        Parameters
        -----------
        content: Optional[:class:`str`]
            The content to send
        embed: Optional[:class:`wharf.Embed`]
            Embed that should or should not be sent
        flags: Optional[:class:`wharf.MessageFlags`]
            Flags that go along with the sent interaction
        file: Optional[:class:`wharf.File`]
            File that should or should not be sent
        type: :class:`int`
            Type that the responded interaction should be
            https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object-interaction-callback-type
        """

        await self.cache.http.interaction_respond(
            self.id,
            self.token,
            type,
            content=content,
            embed=embed,
            flags=flags,
            file=file,
            components=components,
        )

    def _make_options(self):
        if self.payload["data"].get("options"):
            for option in self.payload["data"].get("options"):
                option = InteractionOption(option)
                self.options.append(option)


class InteractionCommand:
    def __init__(self, *, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.options = []

    def add_options(
        self,
        *,
        name: str,
        type: InteractionOptionType,
        description: str,
        choices: Optional[List] = None,
        required: bool = True,
    ):
        data = {
            "name": name,
            "description": description,
            "type": type.value,
            "required": required,
        }

        if choices:
            data["choices"] = choices

        self.options.append(data)

    def _to_json(self):
        payload = {
            "name": self.name,
            "description": self.description,
            "type": 1,
        }

        if self.options:
            payload["options"] = self.options

        return payload

    @classmethod
    def _from_json(cls, payload: Dict[str, Any]):
        name = payload["data"]["name"]
        description = payload["data"].get("description", "")

        return cls(name=name, description=description)
