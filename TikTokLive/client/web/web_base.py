import asyncio
import signal
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from typing import Optional, Any, Awaitable

from httpx import Cookies, AsyncClient, Response

from TikTokLive.client.web import web_defaults


class WebcastHTTPClient:
    _uuc: int = 0
    _lib: str = "ttlive-python"

    def __init__(
            self,
            loop: AbstractEventLoop,
            httpx_kwargs: dict = {},
            sign_api_key: Optional[str] = None
    ):
        self._uuc += 1
        self._httpx: AsyncClient = self._create_httpx_client(sign_api_key, httpx_kwargs)
        self._loop: AbstractEventLoop = loop

        self._loop.add_signal_handler(
            signal.SIGTERM,
            lambda: asyncio.create_task(self.close())
        )

    async def close(self):
        await self._httpx.aclose()

    def _create_httpx_client(self, sign_api_key: str, httpx_kwargs: dict) -> AsyncClient:
        self.cookies = httpx_kwargs.pop("cookies", Cookies())
        self.headers = {**httpx_kwargs.pop("headers", {}), **web_defaults.DEFAULT_REQUEST_HEADERS}

        self.params = {
            "apiKey": sign_api_key,
            **httpx_kwargs.pop("params", {}), **web_defaults.DEFAULT_CLIENT_PARAMS
        }

        return AsyncClient(
            cookies=self.cookies,
            params=self.params,
            headers=self.headers,
            **httpx_kwargs
        )

    async def get_response(
            self,
            url: str,
            extra_params: dict = {},
            extra_headers: dict = {},
            **kwargs
    ) -> Response:
        self.params["uuc"] = self._uuc

        return await self._httpx.get(
            url=url,
            cookies=self.cookies,
            params={**self.params, **extra_params},
            headers={**self.headers, **extra_headers},
            **kwargs
        )

    async def get_json(self, url: str, extra_params: Optional[dict] = None, **kwargs) -> Optional[dict]:
        response: Response = await self.get_response(url, extra_params, **kwargs)
        return response.json()
        # remember to .get("data") when using

    def __del__(self):
        self._uuc = max(0, self._uuc - 1)



class WebcastRoute(ABC):

    def __init__(self, web: WebcastHTTPClient):
        self._web: WebcastHTTPClient = web

    @abstractmethod
    def __call__(self, **kwargs: Any) -> Awaitable[Any]:
        raise NotImplementedError
