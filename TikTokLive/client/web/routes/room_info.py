from typing import Any, Dict, Optional

from httpx import Response

from TikTokLive.client.web.web_base import WebcastRoute
from TikTokLive.client.web.web_defaults import TIKTOK_URL_WEBCAST


class FailedFetchRoomInfoError(RuntimeError):
    pass


class RoomInfoRoute(WebcastRoute):
    """Retrieve the room ID"""

    PATH: str = TIKTOK_URL_WEBCAST + "/room/info/"

    async def __call__(self, room_id: Optional[str] = None) -> Dict[str, Any]:

        try:

            response: Response = await self._web.get_response(
                url=self.PATH,
                extra_params={"room_id": room_id or self._web.params["room_id"]}
            )

            return response.json()["data"]

        except Exception as ex:
            raise FailedFetchRoomInfoError from ex
