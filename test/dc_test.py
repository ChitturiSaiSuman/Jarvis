from src.integrations.discord.bot import Bot
from src.common import config
import discord

token = config.Constants.creds['jarvis']['bot']['token']
bot = Bot(intents=discord.Intents.all())
bot.run(token)
