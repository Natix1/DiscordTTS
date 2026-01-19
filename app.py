import asyncio
import app_shared

from tts_worker import tts_worker
from bot_worker import discord_bot_worker

# THIS NEEDS PYTHON 3.13


async def main():
    tts_task = asyncio.create_task(tts_worker())
    bot_task = asyncio.create_task(discord_bot_worker())

    try:
        await asyncio.Future()
    except (KeyboardInterrupt, asyncio.CancelledError):
        print("\nShutting down...")
    finally:
        if app_shared.voice_client is not None:
            print("Disconnecting from voice...")
            try:
                await asyncio.wait_for(
                    app_shared.voice_client.disconnect(force=True), timeout=2.0
                )
                print("Disconnected.")
            except Exception as e:
                print(f"Error during disconnect: {e}")

        tts_task.cancel()
        bot_task.cancel()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
