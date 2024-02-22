from httpx import Response

from TikTokLive.client.web.web_base import WebcastRoute


class ImageFetchRoute(WebcastRoute):

    async def __call__(self, image_url: str) -> bytes:
        response: Response = await self._web.get_response(
            url=image_url
        )

        return response.read()
