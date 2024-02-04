from typing import Type, Union

from .custom_events import *
from .proto_events import *

Event: Type = Union[CustomEvent]