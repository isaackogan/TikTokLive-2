import asyncio

from TikTokLive.client.client import TikTokLiveClient
from TikTokLive.client.logger import LogLevel
from TikTokLive.events import ConnectEvent, CommentEvent

client: TikTokLiveClient = TikTokLiveClient(
    unique_id="@grndpagaming"
)


@client.on(ConnectEvent)
async def on_connect(_: ConnectEvent):
    print('Connected')


@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    print(f"{event.user.unique_id} -> {event.comment}")


if __name__ == '__main__':
    client.logger.setLevel(LogLevel.INFO.value)


    async def main():
        await client.connect()
        while True:
            await asyncio.sleep(1)


    asyncio.get_event_loop().run_until_complete(main())
