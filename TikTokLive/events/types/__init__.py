from typing import Type, Union

from .custom_events import CustomEvent
from .proto_events import ProtoEvent

Event: Type = Union[ProtoEvent, CustomEvent]
