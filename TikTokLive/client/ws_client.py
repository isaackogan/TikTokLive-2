import asyncio
import signal
from asyncio import AbstractEventLoop
from typing import Optional, AsyncIterator

import websockets as websockets
from websockets import WebSocketClientProtocol

from TikTokLive.proto import WebcastWebsocketAck, WebcastPushFrame


class WebsocketClient:

    def __init__(self):
        self._connected: bool = False
        self._websocket: Optional[WebSocketClientProtocol] = None
        self._loop: AbstractEventLoop = asyncio.get_running_loop()

    @property
    def ws_kwargs(self) -> dict:
        return {}

    async def send_ack(self, message_id: int) -> None:

        # Can't ack a dead websocket...
        if not self._websocket or not self._websocket.open:
            return

        message: WebcastWebsocketAck = WebcastWebsocketAck(
            type="ack",
            id=message_id
        )

        await self._websocket.send(bytes(message))

    async def connect_ws(self) -> AsyncIterator[WebcastPushFrame]:
        """

        The iterator exits normally when the connection is closed with close code
        1000 (OK) or 1001 (going away) or without a close code. It raises
        a :exc:`~websockets.exceptions.ConnectionClosedError` when the connection
        is closed with any other code.
        TODO handle this TODO
        """

        async for websocket in websockets.connect(**self.ws_kwargs):

            try:

                # Graceful closing
                self._loop.add_signal_handler(signal.SIGTERM, self._loop.create_task, websocket.close())

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
