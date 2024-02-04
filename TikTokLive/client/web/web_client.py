from TikTokLive.client.web.routes.gift_list import GiftListRoute
from TikTokLive.client.web.routes.room_id import RoomIdRoute
from TikTokLive.client.web.routes.room_info import RoomInfoRoute
from TikTokLive.client.web.routes.sign_fetch import SignFetchRoute
from TikTokLive.client.web.web_base import WebcastHTTPClient


class WebcastWebClient(WebcastHTTPClient):
    """
    Wrapper for the HTTP client to add web routes

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.fetch_room_id: RoomIdRoute = RoomIdRoute(self)
        self.fetch_sign_fetch: SignFetchRoute = SignFetchRoute(self)
        self.fetch_room_info: RoomInfoRoute = RoomInfoRoute(self)
        self.fetch_gift_list: GiftListRoute = GiftListRoute(self)
