from __future__ import annotations

import asyncio
import inspect
import logging
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, TypeVar, Optional

from .impl import Interaction, Member, Message

if TYPE_CHECKING:
    from .impl.cache import Cache


EventT = TypeVar("EventT")
T = TypeVar("T")
Func = Callable[..., T]
CoroFunc = Func[Coroutine[Any, Any, Any]]

_log = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, cache: Cache):
        self.events: Dict[str, List[CoroFunc]] = {}
        self.cache = cache

    def filter_events(self, event_type: EventT, event_data):
        if event_data is None:
            raise ValueError("event data cannot be None")

        if event_type in ("message_create", "message_update"):
            if event_type == "message_update" and len(event_data) == 4:
                return

            return Message(event_data, self.cache)

        elif event_type == "interaction_create":
            return Interaction(self.cache, event_data)

        elif event_type in ("guild_member_add", "guild_member_remove"):
            return Member(event_data, self.cache)

        elif event_type == "ready":
            return None

        return event_data

    def add_callback(self, event_name, func: CoroFunc):
        if event_name not in self.events:
            raise ValueError("Event not in any known events!")

        self.events[event_name].append(func)

    def add_event(self, event_name: str):
        self.events[event_name] = []

    def subscribe(self, event_name: str, func: CoroFunc):
        self.events[event_name] = [func]

        _log.info("Subscribed to %r", event_name)

    def get_event(self, event_name: str):
        return self.events.get(event_name)

    def dispatch(self, event_name: str, *args, **kwargs):
        event = self.get_event(event_name)
        
        if event is None:
            raise ValueError("Event not in any events known :(")        

        data = self.filter_events(event_name, *args)

    
        for callback in event:
            if data is None:
                asyncio.create_task(callback())
            else:
                asyncio.create_task(callback(data))

        _log.info("Dispatched event %r", event_name)


