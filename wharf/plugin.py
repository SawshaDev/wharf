from __future__ import annotations

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

if TYPE_CHECKING:
    from .bot import Bot

T = TypeVar("T")
Func = Callable[..., T]
CoroFunc = Func[Coroutine[Any, Any, Any]]


class Plugin:
    def __init__(self, *, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description

        self._listeners: Dict[str, CoroFunc] = defaultdict(list)

        self._bot: Optional[Bot] = None

    @property
    def bot(self):
        if self._bot is None:
            raise RuntimeError("Bot cannot be accessed here before its added!")

        return self._bot

    @bot.setter
    def bot(self, bot: Bot):
        self._bot = bot

    def listen(self, event_name: str):
        def inner(func: CoroFunc):
            self._listeners[event_name].append(func)

            return func

        return inner

    @property
    def listeners(self) -> Dict[str, List[CoroFunc]]:
        return self._listeners
