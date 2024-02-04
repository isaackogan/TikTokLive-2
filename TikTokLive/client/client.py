import asyncio
import logging
import urllib.parse
from asyncio import AbstractEventLoop, Task, CancelledError
from logging import Logger
from typing import Optional, Type, AsyncIterator, Dict, Any, Tuple, Union, Callable, TypeVar

from httpx import Proxy
from httpx._types import ProxiesTypes
from pyee import AsyncIOEventEmitter
from pyee.base import Handler

from TikTokLive.client.errors import AlreadyConnectedError, UserOfflineError, InitialCursorMissingError, \
    WebsocketURLMissingError
from TikTokLive.client.logger import TikTokLiveLogHandler, LogLevel
from TikTokLive.client.web import web_defaults
from TikTokLive.client.web.web_client import WebcastWebClient
from TikTokLive.client.ws.ws_client import WebcastWSClient
from TikTokLive.events import Event
from TikTokLive.events.custom_events import UnknownEvent, ConnectEvent
from TikTokLive.events.proto_events import EVENT_MAPPINGS, ProtoEvent
from TikTokLive.proto import WebcastResponse, WebcastResponseMessage

EventHandler = TypeVar("EventHandler", bound=Callable[[Event], None])


class TikTokLiveClient(AsyncIOEventEmitter):

    def __init__(
            self,
            unique_id: str,
            sign_api_key: Optional[str] = None,
            proxy: Optional[Proxy] = None,
            web_kwargs: dict = {},
            ws_kwargs: dict = {},
    ):
        super().__init__()

        self._ws: WebcastWSClient = WebcastWSClient(
            ws_kwargs=ws_kwargs,
            proxy=proxy
        )

        self._web: WebcastWebClient = WebcastWebClient(
            httpx_kwargs=web_kwargs,
            proxy=proxy,
            sign_api_key=sign_api_key
        )

        self._logger: Logger = TikTokLiveLogHandler.get_logger(
            level=LogLevel.ERROR
        )

        # Properties
        self._unique_id: str = self.parse_unique_id(unique_id)
        self._room_id: Optional[str] = None
        self._room_info: Optional[Dict[str, Any]] = None
        self._gift_info: Optional[Dict[str, Any]] = None
        self._event_loop_task: Optional[Task] = None

    @classmethod
    def parse_unique_id(cls, unique_id: str) -> str:
        """
        Parse unique ID from a generic string

        :param unique_id: The unique_id to parse
        :return: The parsed unique_id

        """

        return unique_id \
            .replace(web_defaults.TIKTOK_URL_WEB + "/", "") \
            .replace("/live", "") \
            .replace("@", "", 1) \
            .strip()

    async def start(
            self,
            *,
            process_connect_events: bool = True,
            fetch_room_info: bool = True,
            fetch_gift_info: bool = False
    ) -> Task:
        """
        Create a non-blocking connection to TikTok LIVE and return the task

        :param process_connect_events: Whether to process initial events sent on room join
        :param fetch_room_info: Whether to fetch room info on join
        :param fetch_gift_info: Whether to fetch gift info on join
        :return: Task containing the heartbeat of the client

        """

        if self._ws.connected:
            raise AlreadyConnectedError("You can only make one connection per client!")

        # <Required> Fetch room ID
        self._room_id: str = await self._web.fetch_room_id(self._unique_id)

        # <Optional> Fetch room info
        if fetch_room_info:
            self._room_info = await self._web.fetch_room_info()
            if self._room_info.get("status", 4) == 4:
                raise UserOfflineError()

        # <Optional> Fetch gift info
        if fetch_gift_info:
            self._gift_info = await self._web.fetch_gift_list()

        # <Required> Fetch the first response
        webcast_response: WebcastResponse = await self._web.fetch_sign_fetch()

        # <Optional> Disregard initial events
        webcast_response.messages = webcast_response.messages if process_connect_events else []

        # Handle detection & invalid payloads
        if not webcast_response.cursor:
            raise InitialCursorMissingError("Missing cursor in initial fetch response.")
        if not webcast_response.push_server:
            raise WebsocketURLMissingError("No websocket URL received from TikTok.")
        if not webcast_response.route_params_map:
            raise WebsocketURLMissingError("Websocket parameters missing.")

        # Start the websocket connection & return it
        self._event_loop_task = self._asyncio_loop.create_task(self._client_loop(webcast_response))
        return self._event_loop_task

    async def connect(self, **kwargs: Any) -> Task:
        """
        Start a future-blocking connection to TikTokLive

        :param kwargs: Kwargs to pass to start
        :return: The task, once it's finished

        """

        task: Task = await self.start(**kwargs)

        try:
            await task
        except CancelledError:
            self._logger.debug("The client has been manually stopped with 'client.stop()'.")

        return task

    def run(self, **kwargs: Any) -> Task:
        """
        Start a thread-blocking connection to TikTokLive

        :param kwargs: Kwargs to pass to start
        :return: The task, once it's finished

        """

        return self._asyncio_loop.run_until_complete(self.connect(**kwargs))

    async def disconnect(self) -> None:
        """
        Disconnect the client from the websocket

        :return: None

        """

        # Wait gracefully for things to finish
        await self._ws.disconnect()
        await self._event_loop_task

        # Reset state vars
        self._room_id = None
        self._room_info = None
        self._gift_info = None
        self._event_loop_task = None

    async def _client_loop(self, initial_response: WebcastResponse) -> None:
        """Run the main client loop to handle events"""

        async for event in self._ws_loop(initial_response):

            if event is None:
                continue

            self._logger.debug(f"Received Event '{event.type}'.")
            self.emit(event.type, event)

    async def _ws_loop(self, initial_response: WebcastResponse) -> AsyncIterator[Optional[Event]]:
        """Run the websocket loop to handle incoming WS messages"""

        # Handle initial messages
        for webcast_message in initial_response.messages:
            yield self._parse_webcast_response(webcast_message)

        first_event: bool = True

        # Handle websocket connection
        async for response_message in self._ws.connect(*self._build_connect_info(initial_response)):

            if first_event:
                yield ConnectEvent(unique_id=self._unique_id, room_id=self._room_id)
                first_event = False

            yield self._parse_webcast_response(response_message)

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
        return super(TikTokLiveClient, self).on(event.get_type(), f)

    def add_listener(self, event: Type[Event], f: EventHandler) -> Handler:
        return super().add_listener(event=event.get_type(), f=f)

    def _parse_webcast_response(self, response: Optional[WebcastResponseMessage]) -> Optional[Event]:
        """Parse incoming webcast responses"""

        if response is None:
            self._logger.warning("Received a null response from the Webcast server.")
            return None

        event_type: Optional[Type[ProtoEvent]] = EVENT_MAPPINGS.get(response.method)

        if not event_type:
            return UnknownEvent().from_pydict(response.to_dict())

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

    @property
    def connected(self) -> bool:
        return self._ws.connected

    @property
    def logger(self) -> logging.Logger:
        return self._logger
