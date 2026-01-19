import app_shared
import discord

from discord.ext import commands
from app_shared import discord_bot

bound_to = []


def is_allowed_user():
    async def predicate(ctx):
        return ctx.author.id in app_shared.OWNER_USER_IDS

    return commands.check(predicate)


def parse_id(id: str):
    try:
        id_int = int(id)
        return id_int

    except ValueError:
        # <@id>
        parsed = int(id[2 : len(id) - 1])
        return parsed


async def reply_with_bound_to(message: discord.Message):
    bound_to_str = []
    for user_id in bound_to:
        bound_to_str.append(f"<@{user_id}>")

    if len(bound_to_str) == 0:
        await message.reply("Currently bound to nobody")
    else:
        await message.reply(f"Current bound to: {','.join(bound_to_str)}")


@discord_bot.command(name="join", description="Joins the current channels' voice chat.")
@is_allowed_user()
async def join(ctx: commands.Context):
    if not (
        isinstance(ctx.message.channel, discord.channel.GroupChannel)
        or isinstance(ctx.message.channel, discord.channel.VoiceChannel)
    ):
        await app_shared.error_message_reply(ctx.message, "run it in a voice channel")
        return

    try:
        await app_shared.set_reaction(ctx.message, "🔃")
        app_shared.voice_client = await ctx.message.channel.connect(
            timeout=20,
            reconnect=True,
            ring=False,  # type: ignore
        )

        if app_shared.voice_client.is_connected():
            await app_shared.set_reaction(ctx.message, "✅")
            await discord_bot.change_voice_state(
                self_deaf=True, channel=ctx.message.channel
            )

    except ValueError as e:
        await app_shared.error_message_reply(ctx.message, f"failed parsing int: {e}")
    await reply_with_bound_to(ctx.message)


@discord_bot.command(
    name="bind",
    description="Binds to the given user. Can be either a user id or a mention.",
)
@is_allowed_user()
async def bind(ctx: commands.Context, id: str):
    try:
        bound_to.append(parse_id(id))
    except ValueError as e:
        await app_shared.error_message_reply(
            ctx.message, f"failed appending user id: {e}"
        )
        return

    await reply_with_bound_to(ctx.message)


@discord_bot.command(
    name="unbind",
    description="Unbinds from the given user. Can be either a user id or a mention.",
)
@is_allowed_user()
async def unbind(ctx: commands.Context, id: str):
    try:
        index = bound_to.index(parse_id(id))
    except ValueError as e:
        await app_shared.error_message_reply(
            ctx.message,
            f"failed removing {id}. likely wasnt in the list in the first place. error: {e}",
        )
        return

    bound_to.pop(index)
    await app_shared.set_reaction(ctx.message, "✅")
    await reply_with_bound_to(ctx.message)


@discord_bot.command(
    name="disconnect",
    description="Disconnects from the voice channel, if in one already.",
)
@is_allowed_user()
async def disconnect(ctx: commands.Context):
    if app_shared.voice_client is not None:
        await app_shared.voice_client.disconnect(force=True)
        await app_shared.set_reaction(ctx.message, "✅")

        bound_to.clear()


@discord_bot.command(name="bound", description="Lists all bound users.")
@is_allowed_user()
async def bound(ctx: commands.Context):
    await reply_with_bound_to(ctx.message)


@discord_bot.command(name="voices", description="Lists all available voices.")
@is_allowed_user()
async def voices(ctx: commands.Context):
    await ctx.reply(", ".join(app_shared.all_voices))


@discord_bot.command(name="setvoice", description="Sets the current voice.")
@is_allowed_user()
async def set_voice(ctx: commands.Context, voice: str):
    if voice not in app_shared.all_voices:
        await app_shared.error_message_reply(ctx.message, "invalid voice")
        return

    app_shared.current_voice = voice
    await app_shared.set_reaction(ctx.message, "✅")


@discord_bot.command(name="setspeed", description="Sets the voice's speed.")
@is_allowed_user()
async def setspeed(ctx: commands.Context, speed_str: str):
    try:
        speed = float(speed_str)
        if not (speed >= 0.5 and speed <= 2.0):
            await app_shared.error_message_reply(
                ctx.message, "speed must be between 0.5 and 2.0"
            )
            return

        app_shared.voice_speed = speed
    except ValueError as e:
        await app_shared.error_message_reply(
            ctx.message, f"failed to parse out the float: {e}"
        )
        return


@discord_bot.command(name="voice", description="Shows the current voice.")
@is_allowed_user()
async def voice(ctx: commands.Context):
    await ctx.reply(f"current voice: {app_shared.voice or 'none'}")


@discord_bot.command(
    name="addowner",
    description="Adds an owner; gives access to all commands. Temporary. For permament owners, update .env.",
)
@is_allowed_user()
async def add_owner(ctx: commands.Context, owner: str):
    try:
        app_shared.OWNER_USER_IDS.append(parse_id(owner))
    except ValueError as e:
        await app_shared.error_message_reply(
            ctx.message, f"failed parsing out value: {e}"
        )


@discord_bot.command(
    name="removeowner", description="Removes an owner; takes access from all commands."
)
@is_allowed_user()
async def remove_owner(ctx: commands.Context, owner: str):
    try:
        owner_id = parse_id(owner)
    except ValueError as e:
        print(f"failed parsing out id: {e}")
        return

    try:
        app_shared.OWNER_USER_IDS.remove(owner_id)
    except ValueError as e:
        print(f"failed removing owner: {e}")
        return


@discord_bot.command(name="reactionson", description="Turns on message reactions.")
@is_allowed_user()
async def reactions_on(ctx: commands.Context):
    app_shared.REACTIONS_ENABLED = True
    await app_shared.set_reaction(ctx.message, "✅")


@discord_bot.command(name="reactionsoff", description="Turns off message reactions.")
@is_allowed_user()
async def reactions_off(ctx: commands.Context):
    await app_shared.set_reaction(ctx.message, "👋")
    app_shared.REACTIONS_ENABLED = False


@discord_bot.command(name="commands", description="Lists all commands")
@is_allowed_user()
async def commands_command(ctx: commands.Context):
    full_str = ""
    index = 1
    for command in app_shared.discord_bot.commands:
        full_str += f"## {index}. {command.name}\n"
        if len(command.description) > 0:
            full_str += f"{command.description}"
        else:
            full_str += "(no description)"

        full_str += "\n"
        index += 1

    await ctx.reply(full_str)


@discord_bot.event
async def on_message(message: discord.Message):
    ctx = await discord_bot.get_context(message)
    await discord_bot.invoke(ctx)

    if ctx.command is not None:
        return

    if message.author.id not in bound_to:
        return

    await app_shared.tts_queue.put(message)


@discord_bot.event
async def on_ready():
    assert discord_bot.user
    print(f"logged in as {discord_bot.user.name}")

    discord_bot.remove_command("help")


async def discord_bot_worker():
    await app_shared.discord_bot.start(app_shared.TOKEN)
