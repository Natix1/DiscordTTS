import app_shared
import discord
import atexit

from typing import Optional


class QueuedTTS:
    text: str
    discord_message: discord.Message


class BotWorker(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bound_to: list[int] = []

    async def reply_with_bound_to(self, message: discord.Message):
        bound_to_str = []
        for user_id in self.bound_to:
            bound_to_str.append(str(user_id))

        if len(bound_to_str) == 0:
            await message.reply("Currently bound to nobody")
        else:
            await message.reply(f"Current bound to: {','.join(bound_to_str)}")

    async def on_ready(self):
        assert self.user
        print(f"logged in as {self.user.name}")

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        parts = message.content.split(" ")
        if parts[0].lower() == "!join":
            if not (
                isinstance(message.channel, discord.channel.GroupChannel)
                or isinstance(message.channel, discord.channel.VoiceChannel)
            ):
                await app_shared.error_message_reply(
                    message, "run it in a voice channel"
                )
                return

            try:
                await app_shared.set_reaction(message, "🔃")
                app_shared.voice_client = await message.channel.connect(
                    timeout=20, reconnect=True
                )

                if app_shared.voice_client.is_connected():
                    await app_shared.set_reaction(message, "✅")
                    await self.change_voice_state(
                        self_deaf=True, channel=message.channel
                    )

            except ValueError as e:
                await app_shared.error_message_reply(
                    message, f"failed parsing int: {e}"
                )
            await self.reply_with_bound_to(message)

        elif parts[0].lower() == "!bind":
            if len(parts) < 2:
                await app_shared.error_message_reply(message, "not enough params")
                return

            self.bound_to.append(int(parts[1]))
            await self.reply_with_bound_to(message)

        elif parts[0].lower() == "!unbind":
            if len(parts) < 2:
                await app_shared.error_message_reply(message, "not enough params")
                return

            try:
                index = self.bound_to.index(int(parts[1]))
            except ValueError as e:
                await app_shared.error_message_reply(
                    message,
                    f"failed removing {parts[1]}. likely wasnt in the list in the first place. error: {e}",
                )
                return

            self.bound_to.pop(index)
            await app_shared.set_reaction(message, "✅")
            await self.reply_with_bound_to(message)

        elif parts[0].lower() == "!disconnect":
            if self.voice_client is not None:
                await self.voice_client.disconnect(force=True)
                await app_shared.set_reaction(message, "✅")

            self.bound_to.clear()

        elif parts[0].lower() == "!bound":
            await self.reply_with_bound_to(message)

        elif message.author.id in self.bound_to:
            queued = QueuedTTS()
            queued.text = message.content
            queued.discord_message = message

            await app_shared.tts_queue.put(queued)
