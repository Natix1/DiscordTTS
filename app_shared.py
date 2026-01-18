import os
import asyncio
import discord

from dotenv import load_dotenv
from app_types import QueuedTTS, BotWorker
from typing import Optional

load_dotenv()


def env_assert(key: str) -> str:
    value = os.getenv(key)
    assert value, "value not found"

    return value


TOKEN = env_assert("TOKEN")
OWNER_USER_ID = int(env_assert("OWNER_USER_ID"))

tts_queue: asyncio.Queue[QueuedTTS] = asyncio.Queue()
voice_client: Optional[discord.VoiceClient] = None
discord_client = BotWorker()


async def set_reaction(message: discord.Message, reaction: str):
    assert discord_client.user

    for current in message.reactions:
        await current.remove(discord_client.user)

    await message.add_reaction(reaction)


async def error_message_reply(message: discord.Message, error_message: str):
    print(f"errored: {error_message}")

    await set_reaction(message, "❌")
    await message.reply(error_message)
