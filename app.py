import asyncio

from tts_worker import tts_worker
from bot_worker import discord_bot_worker


async def main():
    asyncio.create_task(tts_worker())
    asyncio.create_task(discord_bot_worker())

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    asyncio.run(main())
