from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ...enums import MessageFlags
from ...file import File

if TYPE_CHECKING:
    from ...commands import InteractionCommand, InteractionOption
    from ..cache import Cache
    from ..models import Embed


class Interaction:
    def __init__(self, payload: Dict[str, Any], cache: Cache):
        self.cache = cache
        self._from_data(payload)

    def _from_data(self, payload: Dict[str, Any]) -> None:
        self.id: int = payload["id"]
        self.token: str = payload["token"]
        self.channel_id: int = payload["channel_id"]
        self.type:str  = payload["type"]
        self.command: Optional[InteractionCommand] = None
        self.options: List[InteractionOption] = []

        if self.type == 2:
            self.command = InteractionCommand._from_json(payload["data"])
            if payload['data'].get("options"):
                self.options = self._make_options(payload['data'])

        self.guild_id = int(payload.get("guild_id"))  # type: ignore
        self._member = payload.get("member")

        if self._member:
            self._user = self._member["user"]
        else:
            self._user = payload["user"]


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

    def _make_options(self, data: Dict[str, Any]) -> list[InteractionOption]:
        options: List[InteractionOption] = []

        for option in data["options"]:
            option = InteractionOption(option)
            options.append(option)

        return options        

