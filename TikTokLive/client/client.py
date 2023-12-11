import logging
from logging import Logger
from typing import Optional, Type, AsyncIterator

from pyee import AsyncIOEventEmitter

import TikTokLive.proto as tiktok_proto
from TikTokLive.client.ws_client import WebsocketClient
from TikTokLive.events.types import Event
from TikTokLive.events.types.proto_events import EVENT_MAPPINGS, ProtoEvent
from TikTokLive.proto import WebcastResponse, WebcastResponseMessage


class TikTokLiveClient(AsyncIOEventEmitter):

    def __init__(self):
        super().__init__()
        self._ws: Optional[WebsocketClient] = WebsocketClient()
        self._logger: Logger = logging.getLogger("TikTokLive")

    async def _client_loop(self) -> None:

        async for event_name, event_item in self._ws_loop():
            self._logger.debug(f"Received Event [{event_name}]: {event_item}")
            self.emit(event_name, event_item)

    async def _ws_loop(self) -> AsyncIterator[Event]:

        async for push_frame in self._ws.connect_ws():

            if push_frame.payload_type != "msg":
                self._logger.debug(f"Received Non-Message Frame: {push_frame}")
                continue

            for webcast_message in WebcastResponse().parse(push_frame.payload).messages:

                if webcast_message is None:
                    continue

                yield self._parse_webcast_response(webcast_message)

    def _parse_webcast_response(self, response: WebcastResponseMessage) -> Optional[Event]:

        event_name: Optional[str] = EVENT_MAPPINGS.get(response.method)
        event_type: Optional[Type[ProtoEvent]] = getattr(tiktok_proto, event_name, None)

        # TODO custom events go here!

        if not event_type:
            self._logger.warning(f"Failed to parse webcast response: {response}")
            return None

        return event_type().parse(response.payload)
