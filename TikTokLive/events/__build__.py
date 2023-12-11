from typing import List, get_type_hints, Dict

import betterproto

from TikTokLive import proto
from TikTokLive.proto import Common

MESSAGE_OVERRIDES: Dict[str, str] = {
    "WebcastMsgDetectMessage": "MessageDetectEvent"
}


class EventsTranscriber:

    def __init__(
            self,
            template_dir: str,
            template_name: str,
            output_path: str
    ):

        self._env: jinja2.Environment = jinja2.Environment(
            trim_blocks=True,
            lstrip_blocks=True,
            loader=jinja2.FileSystemLoader(template_dir),
        )

        self._template: jinja2.Template = self._env.get_template(template_name)
        self._output_path: str = output_path

    def __call__(self, *args, **kwargs):

        output: str = self._template.render(**self.get_config())

        with open(self._output_path, "w", encoding="utf-8") as file:
            file.write(output)

    def get_config(self) -> dict:
        events: List[dict] = []

        for name, item in proto.__dict__.items():

            # Must be a betterproto message
            try:
                if not issubclass(item, betterproto.Message):
                    continue
            except TypeError:
                continue

            hints: dict = get_type_hints(item)

            # Must start with "Webcast"
            if not name.startswith("Webcast"):
                continue

            # Only Events have a common
            if not hints.get('common'):
                continue

            # Check, just in case...
            if not issubclass(hints['common'], Common):
                continue

            # Now we can generate code for it
            events.append(
                {
                    "event_name": self.event_name(name),
                    "subclass_name": name,
                }
            )

        return {
            "events": events,
            "proto_pkg": "TikTokLive.proto",
            "event_pkg": "...events.event"
        }

    def event_name(self, subclass_name: str) -> str:

        # Handle Overrides
        if subclass_name in MESSAGE_OVERRIDES:
            return MESSAGE_OVERRIDES[subclass_name]

        # Handle Generation
        return subclass_name \
            .replace("Message", "Event") \
            .replace("Webcast", "")


if __name__ == '__main__':
    import jinja2

    EventsTranscriber(
        template_dir="./",
        template_name="template_events.jinja2",
        output_path="types/proto_events.py",
    )()
