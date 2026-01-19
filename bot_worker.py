import app_shared
import discord


def has_access(user: discord.User | discord.Member):
    return user.id == 955090007335530506


async def discord_bot_worker():
    await app_shared.discord_client.start(app_shared.TOKEN)
