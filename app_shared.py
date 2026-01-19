import os
import asyncio
import discord

from dotenv import load_dotenv
from typing import Optional
from kokoro_onnx import Kokoro
from discord.ext import commands

load_dotenv()


def env_assert(key: str) -> str:
    value = os.getenv(key)
    assert value, "value not found"

    return value


def get_owner_user_ids() -> list[int]:
    ids = []

    for part in env_assert("OWNER_USER_IDS").split(","):
        try:
            int_part = int(part)
            ids.append(int_part)
        except ValueError as e:
            print(f"failed parsing id '{part}': {e}. Not adding to owners list")

    return ids


TOKEN = env_assert("TOKEN")
OWNER_USER_IDS = get_owner_user_ids()
REACTIONS_ENABLED = env_assert("REACTIONS_ENABLED") == "TRUE"

tts_queue: asyncio.Queue[discord.Message] = asyncio.Queue()
voice_client: Optional[discord.VoiceClient] = None
discord_bot = commands.Bot(
    command_prefix="!",
)
kokoro = Kokoro(
    model_path="models/kokoro-v1.0.onnx",
    voices_path="models/voices-v1.0.bin",
)
current_voice: Optional[str] = "bm_lewis"
voice_speed: float = 1.0
next_requested: bool = False

all_voices = []
for voice in kokoro.voices:
    all_voices.append(voice)


async def set_reaction_yield(message: discord.Message, reaction: str):
    assert discord_bot.user

    if not REACTIONS_ENABLED:
        return

    for current in message.reactions:
        await current.remove(discord_bot.user)

    await message.add_reaction(reaction)


async def set_reaction(message: discord.Message, reaction: str):
    asyncio.create_task(set_reaction_yield(message, reaction))


async def error_message_reply_yield(message: discord.Message, error_message: str):
    print(f"error message reply: {error_message}")

    await set_reaction(message, "❌")
    await message.reply(error_message)


async def error_message_reply(message: discord.Message, error_message: str):
    asyncio.create_task(error_message_reply_yield(message, error_message))
