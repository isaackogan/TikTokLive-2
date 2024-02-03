import asyncio
import logging
import urllib.parse
from asyncio import AbstractEventLoop, Task
from logging import Logger
from typing import Optional, Type, AsyncIterator, Dict, Any, Tuple, Union, Callable, TypeVar

from pyee import AsyncIOEventEmitter
from pyee.base import Handler

from TikTokLive.client.errors import AlreadyConnectedError, UserOfflineError, InitialCursorMissingError, \
    WebsocketURLMissingError
from TikTokLive.client.web.web_client import WebcastWebClient
from TikTokLive.client.ws_client import WebcastWSClient
from TikTokLive.events.types import Event
from TikTokLive.events.types.proto_events import EVENT_MAPPINGS, ProtoEvent
from TikTokLive.proto import WebcastResponse, WebcastResponseMessage

EventHandler = TypeVar("EventHandler", bound=Callable[[Event], None])


class TikTokLiveClient(AsyncIOEventEmitter):

    def __init__(
            self,
            unique_id: str
    ):
        super().__init__()

        # Classes
        self._ws: WebcastWSClient = WebcastWSClient(loop=self._asyncio_loop)
        self._web: WebcastWebClient = WebcastWebClient(loop=self._asyncio_loop)
        self._logger: Logger = logging.getLogger("TikTokLive")

        # Properties
        self._unique_id: str = unique_id
        self._room_id: Optional[str] = None
        self._room_info: Optional[Dict[str, Any]] = None
        self._gift_info: Optional[Dict[str, Any]] = None
        self._event_loop_task: Optional[Task] = None

    async def queue(
            self,
            process_connect_events: bool = True,
            fetch_room_info: bool = True,
            fetch_gift_info: bool = False
    ) -> Task:
        """Start a non-blocking connection to TikTok LIVE"""

        if self._ws.connected:
            raise AlreadyConnectedError("You can only make one connection per client!")

        self._room_id: str = await self._web.fetch_room_id(self._unique_id)
        self._web.params["room_id"] = self._room_id

        if fetch_room_info:
            self._room_info = await self._web.fetch_room_info()
            if self._room_info.get("status", 4) == 4:
                raise UserOfflineError()

        if fetch_gift_info:
            self._gift_info = await self._web.fetch_gift_list()

        webcast_response: WebcastResponse = await self._web.fetch_sign_fetch()

        if not webcast_response.cursor:
            raise InitialCursorMissingError("Missing cursor in initial fetch response.")

        if not webcast_response.push_server:
            raise WebsocketURLMissingError("No websocket URL received from TikTok.")

        if not webcast_response.route_params_map:
            raise WebsocketURLMissingError("Websocket parameters missing.")

        self._web.params["cursor"] = webcast_response.cursor
        self._web.params["internal_ext"] = webcast_response.internal_ext
        webcast_response.messages = webcast_response.messages if process_connect_events else []

        # Start the websocket connection
        self._event_loop_task = self._asyncio_loop.create_task(self._client_loop(webcast_response))

        return self._event_loop_task

    async def start(self, *args, **kwargs) -> Task:
        """Start a future-blocking connection to TikTokLive"""

        task: Task = await self.queue(*args, **kwargs)
        return await task

    def run(self, *args, **kwargs) -> Task:
        """Start a fully blocking connection to TikTokLive"""

        return self._asyncio_loop.run_until_complete(self.start(*args, **kwargs))

    def stop(self) -> None:
        """Stop the client on next ping"""

        self._ws.cancel()
        self._room_id = None
        self._room_info = None
        self._gift_info = None
        self._event_loop_task.cancel(msg="Client stopped.")
        self._event_loop_task = None

    async def _client_loop(self, initial_response: WebcastResponse) -> None:
        """Run the main client loop to handle events"""

        async for event in self._ws_loop(initial_response):

            if event is None:
                continue

            self._logger.debug(f"Received Event: {event.type}")
            self.emit(event.type, event)

    async def _ws_loop(self, initial_response: WebcastResponse) -> AsyncIterator[Optional[Event]]:
        """Run the websocket loop to handle incoming WS messages"""

        # Handle initial messages
        for webcast_message in initial_response.messages:
            yield self._parse_webcast_response(webcast_message)

        # Handle websocket connection
        async for push_frame in self._ws.connect_ws(*self._build_connect_info(initial_response)):
            # TODO on connect event

            if push_frame.payload_type != "msg":
                self._logger.debug(f"Received Non-Message Frame: {push_frame}")
                continue

            for webcast_message in WebcastResponse().parse(push_frame.payload).messages:
                yield self._parse_webcast_response(webcast_message)

    def _build_connect_info(self, initial_response: WebcastResponse) -> Tuple[str, dict]:
        """Create connection info for starting the connection"""

        connect_uri: str = (
                initial_response.push_server
                + "?"
                + urllib.parse.urlencode({**self._web.params, **initial_response.route_params_map})
        )

        connect_headers: dict = {
            "Cookie": " ".join(f"{k}={v};" for k, v in self._web.cookies.items())
        }

        return connect_uri, connect_headers

    def on(self, event: Type[Event], f: Optional[EventHandler] = None) -> Union[Handler, Callable[[Handler], Handler]]:
        """Enforce type hint"""
        return super(TikTokLiveClient, self).on(event.get_type(), f)

    def _parse_webcast_response(self, response: Optional[WebcastResponseMessage]) -> Optional[Event]:
        """Parse incoming webcast responses"""

        if response is None:
            return None

        event_type: Optional[Type[ProtoEvent]] = EVENT_MAPPINGS.get(response.method)

        if not event_type:
            self._logger.warning(f"Failed to parse webcast response: {response}")
            return None

        # TODO custom events reading go here!
        return event_type().parse(response.payload)

    @property
    def room_id(self) -> Optional[str]:
        return self._room_id

    @property
    def room_info(self) -> Optional[Dict[str, Any]]:
        return self._room_info

    @property
    def web(self) -> WebcastWebClient:
        return self._web

    @property
    def _asyncio_loop(self) -> AbstractEventLoop:
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.new_event_loop()
