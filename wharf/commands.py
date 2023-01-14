from __future__ import annotations

from typing import Any, Dict, List, Optional

from .enums import InteractionOptionType


class CommandOption:
    def __init__(self, name: str, description: str, type: int, required: bool):
        self.name = name
        self.description = description
        self.type = type
        self.required = required


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
