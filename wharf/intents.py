from __future__ import annotations

import typing as t
from collections.abc import Callable, Iterator
from functools import reduce
from operator import or_

from typing_extensions import Self

__all__ = (
    "FlagMember",
    "flag",
    "FlagMeta",
    "Flag",
)


class FlagMember:
    def __init__(self, name: str, value: int):
        self._name_ = name
        self._value_ = value

    def __get__(self, instance: t.Optional[Flag], _: type[Flag]) -> t.Union[int, bool]:
        if instance:
            return instance.has(self.value)
        return self.value

    def __set__(self, instance: t.Optional[Flag], toggle: bool) -> None:
        if instance:
            instance.set(self.value, toggle)

    @property
    def name(self) -> str:
        return self._name_

    @property
    def value(self) -> int:
        return self._value_


def flag(func: Callable[..., int]) -> FlagMember:
    return FlagMember(func.__name__, func())


class FlagMeta(type):
    _default_value: int
    __members__: dict[str, FlagMember]

    def __new__(
        cls: type[Self],
        name: str,
        bases: tuple[type, ...],
        classdict: dict[str, t.Any],
        **kwds: t.Any,
    ) -> Self:
        member_map: dict[str, FlagMember] = {
            n: v for n, v in classdict.items() if isinstance(v, FlagMember)
        }

        default_value: int = 0
        if kwds.pop("inverted", False):
            max_bits = max([fm.value for fm in member_map.values()]).bit_length()
            default_value = (2**max_bits) - 1

        ns: dict[str, t.Any] = {
            "__members__": member_map,
            "_default_value": default_value,
            **classdict,
        }

        return super().__new__(cls, name, bases, ns, **kwds)

    @property
    def default_value(cls) -> int:
        return cls._default_value


class Flag(metaclass=FlagMeta):
    value: int
    _default_value: t.ClassVar[int]
    __members__: t.ClassVar[dict[str, FlagMember]]

    def __init__(self, **kwds: bool):
        self.value = type(self).default_value

        for flag_name, enabled in kwds.items():
            if hasattr(self, flag_name) and flag_name in self.__members__:
                self.set(self.__members__[flag_name].value, enabled)
            else:
                raise ValueError(f"Invalid flag member {flag_name}!")

    def set(self, value: int, toggle: bool):
        if toggle:
            self.value |= value
        else:
            self.value &= ~value

    def has(self, value: int):
        return self.value & value == value

    def __iter__(self) -> Iterator[tuple[str, bool]]:
        for name in self.__members__:
            yield name, getattr(self, name)

    @classmethod
    def from_value(cls: type[Self], value: int) -> Self:
        self = cls()
        self.value = value
        return self

    @classmethod
    def all(cls: type[Self]) -> Self:
        member_vals = [f.value for f in cls.__members__.values()]
        all_values = reduce(or_, member_vals)
        return cls.from_value(all_values)

    @classmethod
    def none(cls: type[Self]) -> Self:
        return cls.from_value(cls.default_value)


class Intents(Flag):
    if t.TYPE_CHECKING:

        def __init__(
            self,
            *,
            guilds: bool = ...,
            guild_members: bool = ...,
            guild_bans: bool = ...,
            guild_emojis_and_stickers: bool = ...,
            guild_integrations: bool = ...,
            guild_webhooks: bool = ...,
            guild_invites: bool = ...,
            guild_voice_states: bool = ...,
            guild_presences: bool = ...,
            guild_messages: bool = ...,
            guild_message_reactions: bool = ...,
            guild_message_typing: bool = ...,
            direct_messages: bool = ...,
            direct_message_reactions: bool = ...,
            direct_message_typing: bool = ...,
            message_content: bool = ...,
            guild_scheduled_events: bool = ...,
            auto_moderation_configuration: bool = ...,
            automod_execution: bool = ...,
        ) -> None:
            ...

    @flag
    def GUILDS():
        return 1 << 0

    @flag
    def GUILD_MEMBERS():
        return 1 << 1

    @flag
    def GUILD_BANS():
        return 1 << 2

    @flag
    def GUILD_EMOJIS_AND_STICKERS():
        return 1 << 3

    @flag
    def GUILD_INTEGRATIONS():
        return 1 << 4

    @flag
    def GUILD_WEBHOOKS():
        return 1 << 5

    @flag
    def GUILD_INVITES():
        return 1 << 6

    @flag
    def GUILD_VOICE_STATES():
        return 1 << 7

    @flag
    def GUILD_PRESENCES():
        return 1 << 8

    @flag
    def GUILD_MESSAGES():
        return 1 << 9

    @flag
    def GUILD_MESSAGE_REACTIONS():
        return 1 << 10

    @flag
    def GUILD_MESSAGE_TYPING():
        return 1 << 11

    @flag
    def DIRECT_MESSAGES():
        return 1 << 12

    @flag
    def DIRECT_MESSAGE_REACTIONS():
        return 1 << 13

    @flag
    def DIRECT_MESSAGE_TYPING():
        return 1 << 14

    @flag
    def MESSAGE_CONTENT():
        return 1 << 15

    @flag
    def GUILD_SCHEDULED_EVENTS():
        return 1 << 16

    @flag
    def AUTO_MODERATION_CONFIGURATION():
        return 1 << 20

    @flag
    def AUTO_MODERATION_EXECUTION():
        return 1 << 21

    @classmethod
    def default(cls: type[Self]) -> Self:
        self = cls.all()
        self.GUILD_MEMBERS = False
        self.GUILD_PRESENCES = False
        self.MESSAGE_CONTENT = False
        return self
