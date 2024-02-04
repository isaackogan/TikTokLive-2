from abc import ABC, abstractmethod
from typing import Optional, Any, Awaitable

from httpx import Cookies, AsyncClient, Response, Proxy

from TikTokLive.client.web import web_defaults


class WebcastHTTPClient:
    __uuc: int = 0
    __lib: str = "ttlive-python"

    def __init__(
            self,
            proxy: Optional[Proxy] = None,
            sign_api_key: Optional[str] = None,
            httpx_kwargs: dict = {}
    ):
        self.__uuc += 1

        self._httpx: AsyncClient = self._create_httpx_client(
            proxy,
            sign_api_key,
            httpx_kwargs
        )

    async def close(self):
        await self._httpx.aclose()

    def _create_httpx_client(
            self,
            proxy: Optional[Proxy],
            sign_api_key: str,
            httpx_kwargs: dict
    ) -> AsyncClient:
        self.cookies = httpx_kwargs.pop("cookies", Cookies())
        self.headers = {**httpx_kwargs.pop("headers", {}), **web_defaults.DEFAULT_REQUEST_HEADERS}

        self.params = {
            "apiKey": sign_api_key,
            **httpx_kwargs.pop("params", {}), **web_defaults.DEFAULT_CLIENT_PARAMS
        }

        return AsyncClient(
            proxies=proxy,
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
        self.params["uuc"] = self.__uuc

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
        self.__uuc = max(0, self.__uuc - 1)


class WebcastRoute(ABC):

    def __init__(self, web: WebcastHTTPClient):
        self._web: WebcastHTTPClient = web

    @abstractmethod
    def __call__(self, **kwargs: Any) -> Awaitable[Any]:
        raise NotImplementedError
