import os
import asyncio
import discord

from dotenv import load_dotenv
from app_types import QueuedTTS
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
