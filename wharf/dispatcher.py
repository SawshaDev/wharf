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

from .impl import Interaction, Member, Message

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

    def filter_events(self, event_type: str, event_data: Dict[str, Any]):
        self.event_map = {
            "message_create": Message,
            "message_edit": Message,
            "interaction_create": Interaction,
            "guild_members_add": Member,
            "guild_members_remove": Member,
            "ready": None,
        }

        if event_data is None:
            raise ValueError("Event data CANNOT be None")

        if event_type == "ready":
            return None

        event_object = self.event_map.get(event_type)

        if event_object is None:
            return event_data
        
        return event_object(event_data, self.cache)

    def add_callback(self, event_name: str, func: CoroFunc):
        self.events[event_name].append(func)

        _log.debug("Added callback for %r", event_name)

    def subscribe(self, event_name: str, func: CoroFunc):
        self.add_callback(event_name, func)

        _log.debug("Subscribed to %r", event_name)

    def get_event(self, event_name: str):
        return self.events.get(event_name)

    def dispatch(self, event_name: str, *args):
        event = self.get_event(event_name)

        if event is None:
            raise ValueError("Event not in any events known :(")

        data = self.filter_events(event_name, *args)

        for callback in event:
            if data is None:
                asyncio.create_task(callback())
            else:
                asyncio.create_task(callback(data))

        _log.debug("Dispatched event %r", event_name)
