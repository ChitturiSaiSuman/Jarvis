import interactions, json, asyncio
from src.common import config

async def time_consuming_function(text: str):
    # Perform the time-consuming operation here
    await asyncio.sleep(120)  # Simulating a 2-minute delay
    print(f"Time-consuming operation completed: {text}")

async def say_something(ctx: interactions.CommandContext, text: str):
    print(text)
    asyncio.create_task(time_consuming_function(text))
    await ctx.send(f"You said '{text}'!")

async def pirate(ctx: interactions.CommandContext, text: str):
    print(text)
    await ctx.send(f"From Pirate: '{text}'!")

def run_bot():

    # with open("config.json") as config_file:
    #     config = json.load(config_file)
    #     token = config["token"]

    token = config.Constants.creds['jarvis']['bot']['token']
    bot = interactions.Client(token)

    @bot.command(
        name="say_something",
        description="Say something!",
        options=[
            interactions.Option(
                name="text",
                description="What you want to say",
                type=interactions.OptionType.STRING,
                required=True,
            ),
            interactions.Option(
                name="additional_text",
                description="Additional text to include",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def say_something_handler(ctx: interactions.CommandContext, text: str, additional_text: str = None):
        print(f"Text: {text}, additiona_text: {additional_text}")
        await say_something(ctx, text)

    @bot.command(
        name="pirate",
        description="Add a torrent",
        options=[
            interactions.Option(
                name="text",
                description="Paste magnet URL",
                type=interactions.OptionType.STRING,
                required=True,
            ),
        ],
    )
    async def pirate_handler(ctx: interactions.CommandContext, text: str):
        await pirate(ctx, text)

    @bot.event
    async def on_message(message):
        if message.author.bot:
            return  # Ignore messages from bots
        
        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')

    bot.start()

if __name__ == "__main__":
    run_bot()
