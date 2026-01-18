import asyncio
import wave
import tempfile
import discord

import app_shared
from kokoro_onnx import Kokoro

kokoro = Kokoro(
    model_path="models/kokoro-v1.0.onnx", voices_path="models/voices-v1.0.bin"
)


# most of this jargon is written by mr gpt because uh just look for yourself
# some advanced maths just to play audio
# its scary
# it freaks me out
# but works
async def tts_worker():
    while True:
        queued = await app_shared.tts_queue.get()
        vc = app_shared.voice_client
        if vc is None or not vc.is_connected():
            continue

        audio, sample_rate = kokoro.create(queued.text, "am_adam", 1.0, "en-us")
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
        vc.play(source)

        while vc.is_playing():
            await asyncio.sleep(0.05)
