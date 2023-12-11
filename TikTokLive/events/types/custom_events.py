from typing import Type, Union

from ..event import BaseEvent


class DummyEvent(BaseEvent):
    pass


CustomEvent: Type = Union[DummyEvent]

__all__ = [
    DummyEvent,
    CustomEvent
]