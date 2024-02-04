from dataclasses import dataclass
from typing import Type, Union

from TikTokLive.events.base import BaseEvent
from TikTokLive.proto import WebcastResponseMessage


@dataclass()
class UnknownEvent(WebcastResponseMessage, BaseEvent):
    pass


@dataclass()
class ConnectEvent(BaseEvent):
    unique_id: str
    room_id: str


CustomEvent: Type = Union[UnknownEvent, ConnectEvent]

__all__ = [
    "UnknownEvent",
    "ConnectEvent",
    "CustomEvent"
]
