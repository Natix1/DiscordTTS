import app_shared

from app_shared import TOKEN


async def discord_bot_worker():
    await app_shared.discord_client.start(TOKEN)
