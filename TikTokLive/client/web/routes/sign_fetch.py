import os
from http.cookies import SimpleCookie

from httpx import Response

from TikTokLive.client.web import web_defaults
from TikTokLive.client.web.web_base import WebcastRoute
from TikTokLive.proto import WebcastResponse


class SignAPIError(RuntimeError):
    pass


class SignatureRateLimitError(SignAPIError):
    """
    When a user hits the signature rate limit

    """

    def __init__(self, retry_after: int, reset_time: int, *args):
        """
        Constructor for signature rate limit

        :param retry_after: How long to wait until the next attempt
        :param reset_time: The unix timestamp for when the client can request again
        :param args: Default RuntimeException *args
        :param kwargs: Default RuntimeException **kwargs

        """

        self._retry_after: int = retry_after
        self._reset_time: int = reset_time

        _args = list(args)
        _args[0] = str(args[0]) % str(self.retry_after)
        super().__init__(self, *_args)

    @property
    def retry_after(self) -> int:
        """
        How long to wait until the next attempt

        """

        return self._retry_after

    @property
    def reset_time(self) -> int:
        """
        The unix timestamp for when the client can request again

        """

        return self._reset_time


class SignFetchRoute(WebcastRoute):

    ENV_PATH: str = f"TIKTOKLIVE_SIGN_API_URL"
    PATH: str = os.environ.get(ENV_PATH, web_defaults.TIKTOK_SIGN_API) + "/webcast/fetch/"

    async def __call__(self) -> WebcastResponse:
        response: Response = await self._web.get_response(url=self.PATH)
        data: bytes = await response.aread()

        if response.status_code == 429:
            raise SignatureRateLimitError(
                response.headers.get("RateLimit-Reset"),
                response.headers.get("X-RateLimit-Reset"),
                "You have hit the rate limit for starting connections. Try again in %s seconds. "
                "Catch this error & access its attributes (retry_after, reset_time) for data on when you can "
                "request next."
            )

        elif not data:
            raise SignAPIError(f"Sign API returned an empty request. Are you being detected by TikTok?")

        elif not response.status_code == 200:
            raise SignAPIError(f"Failed request to Sign API with status code {response.status_code}.")

        webcast_response: WebcastResponse = WebcastResponse().parse(response.read())

        # Update web params & cookies
        self._update_cookies(response)
        self._web.params["cursor"] = webcast_response.cursor
        self._web.params["internal_ext"] = webcast_response.internal_ext

        return webcast_response

    def _update_cookies(self, response: Response) -> None:
        """Update the cookies for TikTok"""

        jar: SimpleCookie = SimpleCookie()
        jar.load(response.headers.get("X-Set-TT-Cookie"))

        for cookie, morsel in jar.items():
            self._web.cookies.set(cookie, morsel.value, ".tiktok.com")