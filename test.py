import asyncio

from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.client.web.web_settings import WebDefaults
from TikTokLive.events import ConnectEvent, DisconnectEvent

WebDefaults.tiktok_sign_url = "https://tiktok.eulerstream.com"

client: TikTokLiveClient = TikTokLiveClient(
    unique_id="@tv_asahi_news",
    sign_api_key="2BdEn9S9MEUSfQVaYXOv1W6P1QByQ9tp9U9g7UZBA9J9QRXymotLmK2FLIA84EZPboHEA"
)


@client.on(ConnectEvent)
async def on_connect(_: ConnectEvent):
    print('Connected')
    client.web.fetch_video.start(
        output_fp="output.mp4",
        room_info=client.room_info,
        output_format="mp4"
    )
    await asyncio.sleep(5)
    await client.disconnect()


@client.on(DisconnectEvent)
async def on_disconnect(event: DisconnectEvent):
    print('gotem')


if __name__ == '__main__':
    client.logger.setLevel(LogLevel.INFO.value)


    async def main():
        await client.connect(fetch_gift_info=False)
        while True:
            await asyncio.sleep(1)


    asyncio.get_event_loop().run_until_complete(main())
