class BaseEvent:

    @property
    def event_type(self) -> str:
        return type(self).__name__
