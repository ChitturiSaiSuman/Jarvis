import interactions
from src.common import config

bot = interactions.Client(
    token = config.Constants.creds['jarvis']['bot']['token'],
)

@bot.command(
    name="say_something",
    description="say something!",
    options = [
        interactions.Option(
            name="text",
            description="What you want to say",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def my_first_command(ctx: interactions.CommandContext, text: str):
    print(text)
    await ctx.send(f"You said '{text}'!")

@bot.command(
    name="pirate",
    description="Add a torrent",
    options = [
        interactions.Option(
            name="text",
            description="Paste magnet URL",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def my_second_command(ctx: interactions.CommandContext, text: str):
    print(text)
    await ctx.send(f"From Pirate: '{text}'!")

# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     await message.channel.send("Hello")

bot.start()