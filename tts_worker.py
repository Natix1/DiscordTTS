import asyncio
import wave
import tempfile
import discord
import app_shared

from app_shared import kokoro


# most of this math jargon is written by mr gpt because uh just look for yourself
# some advanced maths just to play audio
# its scary
# it freaks me out
# but works

previous_id = -1


async def tts_worker():
    while True:
        message = await app_shared.tts_queue.get()

        try:
            vc = app_shared.voice_client
            if vc is None or not vc.is_connected():
                await app_shared.error_message_reply(message, "not connected to vc")
                continue

            if not app_shared.current_voice:
                await app_shared.error_message_reply(message, "no voice selected")
                continue

            full_text: str
            if message.author.id == previous_id:
                full_text = message.content
            else:
                full_text = f"{message.author.display_name} said: {message.content}"

            await app_shared.set_reaction(message, "🔃")
            audio, sample_rate = kokoro.create(
                full_text,
                app_shared.current_voice,
                app_shared.voice_speed,
                "en-us",
            )
            if audio.size == 0:
                continue

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
                temp_path = tf.name
            with wave.open(temp_path, "wb") as wf:
                wf.setnchannels(1 if audio.ndim == 1 else audio.shape[1])
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes((audio * 32767).astype("int16").tobytes())

            source = discord.FFmpegPCMAudio(temp_path)
            await app_shared.set_reaction(message, "🔊")
            vc.play(source)

            while vc.is_playing():
                await asyncio.sleep(0.05)

            await app_shared.set_reaction(message, "✅")
        except Exception as e:
            await app_shared.error_message_reply(
                message, f"failed replying to message. error: {e}"
            )
