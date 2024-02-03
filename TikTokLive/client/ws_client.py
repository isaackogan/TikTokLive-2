import asyncio
import functools
import signal
from asyncio import AbstractEventLoop
from typing import Optional, AsyncIterator

import websockets as websockets
from websockets import WebSocketClientProtocol

from TikTokLive.proto import WebcastPushFrame, WebcastResponse


class WebcastWSClient:

    DEFAULT_KWARGS: dict = {
        "subprotocols": ["echo-rptocol"],
        "ping_timeout": 10.0,
        "ping_interval": 10.0
    }

    def __init__(self, loop: AbstractEventLoop, ws_kwargs: dict = {}):
        self._ws_kwargs: dict = ws_kwargs
        self._connected: bool = False
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._loop: AbstractEventLoop = loop
        self._should_cancel: bool = False

    async def send_ack(self, message_id: int) -> None:

        # Can't ack a dead websocket...
        if not self.connected:
            return

        message: WebcastWebsocketAck = WebcastWebsocketAck(
            type="ack",
            id=message_id
        )

        await self._websocket.send(bytes(message))

    @property
    def connected(self) -> bool:
        return self._websocket and self._websocket.open

    def cancel(self):
        self._should_cancel = True

    async def connect_ws(
            self,
            uri: str,
            headers: dict
    ) -> AsyncIterator[WebcastPushFrame]:
        """

        The iterator exits normally when the connection is closed with close code
        1000 (OK) or 1001 (going away) or without a close code. It raises
        a :exc:`~websockets.exceptions.ConnectionClosedError` when the connection
        is closed with any other code.
        TODO handle this TODO
        """

        async for websocket in websockets.connect(
            uri=self._ws_kwargs.pop("uri", uri),
            extra_headers={**headers, **self._ws_kwargs.pop("headers", {})},
            **self._ws_kwargs
        ):

            if self._should_cancel:
                return

            try:

                # Graceful closing
                self._loop.add_signal_handler(
                    signal.SIGTERM,
                    lambda: asyncio.create_task(websocket.close())
                )

                # Each time we receive a message, yield it
                async for message in websocket:
                    yield await self.process_recv(message)

            except websockets.ConnectionClosed:
                # TODO send a warning
                continue

    async def process_recv(self, data: bytes) -> WebcastPushFrame:

        push_reply: WebcastPushFrame = WebcastPushFrame().parse(data)

        if push_reply.log_id > 0:
            await self.send_ack(push_reply.log_id)

        return push_reply
