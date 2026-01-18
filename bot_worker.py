import discord
import app_shared

from app_types import QueuedTTS
from app_shared import TOKEN, OWNER_USER_ID, tts_queue
from typing import Optional


class BotWorker(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bound_to: Optional[int] = None

    async def on_ready(self):
        assert self.user
        print(f"bot ready as {self.user.name}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        parts = message.content.split(" ")
        if parts[0].lower() == "!jointts":
            if not (
                isinstance(message.channel, discord.channel.GroupChannel)
                or isinstance(message.channel, discord.channel.VoiceChannel)
            ):
                await message.add_reaction("❗")
                await message.reply("this aint a voice channel")
                return

            if len(parts) < 2:
                await message.add_reaction("❔")
                await message.reply("not all parameters provided")
                return

            try:
                self.bound_to = int(parts[1])
                print(f"Connecting to {message.channel.name}...")

                app_shared.voice_client = await message.channel.connect(
                    timeout=20, reconnect=True
                )

                if app_shared.voice_client.is_connected():
                    print("Voice successfully connected!")
                    await message.add_reaction("✅")

            except ValueError:
                await message.add_reaction("❌")
        elif parts[0].lower() == "!switchbound":
            if len(parts) < 2:
                await message.add_reaction("❔")
                await message.reply("not all parameters provided")
                return

            self.bound_to = int(parts[1])
        elif parts[0].lower() == "!disconnect":
            if self.voice_client is not None:
                await self.voice_client.disconnect(force=True)
                await message.add_reaction("✅")
                self.bound_to = None

        else:
            if message.author.id != self.bound_to:
                return

            queued = QueuedTTS()
            queued.text = message.content
            queued.discord_message_id = message.id

            await tts_queue.put(queued)


client = BotWorker()


async def discord_bot_worker():
    await client.start(TOKEN)
