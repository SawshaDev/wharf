from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    TypeVar,
)

from .impl import Guild, Interaction, Member, Message

if TYPE_CHECKING:
    from .impl.cache import Cache


T = TypeVar("T")
Func = Callable[..., T]
CoroFunc = Func[Coroutine[Any, Any, Any]]

_log = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, cache: "Cache"):
        self.events: Dict[str, List[CoroFunc]] = defaultdict(list)
        self.cache = cache

        self.event_parsers: Dict[str, Any] = {}

        for attr, func in inspect.getmembers(self):
            if attr.startswith("parse_"):
                self.event_parsers[attr[6:].upper()] = func

    def add_callback(self, event_name: str, func: CoroFunc):
        self.events[event_name].append(func)

        _log.info("Added callback for %r", event_name)

    def subscribe(self, event_name: str, func: CoroFunc):
        self.add_callback(event_name, func)

        _log.info("Subscribed to %r", event_name)

    def get_event(self, event_name: str):
        return self.events.get(event_name)

    def dispatch(self, event_name: str, *args, **kwargs):
        event = self.get_event(event_name)

        if event is None:
            raise ValueError("Event not in any events known :(")

        for callback in event:
            asyncio.create_task(callback(*args, **kwargs))

        _log.info("Dispatched event %r", event_name)

    def parse_ready(self, data):
        self.dispatch("ready")

    def parse_interaction_create(self, data: Dict[str, Any]):
        interaction = Interaction(data, self.cache)

        self.dispatch("interaction_create", interaction)

    def parse_guild_create(self, data: Dict[str, Any]):
        guild = self.cache.add_guild(data)

        self.dispatch("guild_create", guild)

    def parse_message_create(self, data: Dict[str, Any]):
        message = Message(data, self.cache)

        self.dispatch("message_create", message)