from typing import Any, Dict, Optional

from httpx import Response

from TikTokLive.client.web.web_base import WebcastRoute
from TikTokLive.client.web.web_defaults import TIKTOK_URL_WEBCAST


class FailedFetchGiftListError(RuntimeError):
    pass


class GiftListRoute(WebcastRoute):
    """Retrieve the room ID"""

    PATH: str = TIKTOK_URL_WEBCAST + "/gift/list/"

    async def __call__(self, room_id: Optional[str] = None) -> Dict[str, Any]:

        try:
            response: Response = await self._web.get_response(url=self.PATH)
            return response.json()["data"]
        except Exception as ex:
            raise FailedFetchGiftListError from ex
