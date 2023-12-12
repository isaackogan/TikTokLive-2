import asyncio
import signal
from asyncio import AbstractEventLoop

import httpx
from httpx import AsyncClient


class AsyncHTTPClient:

    _uuc: int = 0
    _lib: str = "ttlive-python"

    def __init__(self):
        self._loop: AbstractEventLoop = asyncio.get_running_loop()
        self._http_client: AsyncClient = AsyncClient()
        self._loop.add_signal_handler(signal.SIGTERM, self._loop.create_task, self.close())

    async def close(self):
        await self._http_client.aclose()

    async def __post_bytes(self, url: str, params: dict, **kwargs):

        response: httpx.Response = await self._http_client.get(

        )




