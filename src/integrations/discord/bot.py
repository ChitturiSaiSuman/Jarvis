#!/usr/bin/python3

import asyncio
import logging

import discord

from src.common.config import Constants
from src.integrations.discord.command_matrix import CommandMatrix
from src.services.informio import Informio


class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.informio = Informio()
        self.cmd_matrix = CommandMatrix()

    async def on_ready(self):
        ready_message = 'We have logged in as {0.user}'.format(self)
        logging.info(ready_message)
        print(ready_message)

    async def on_message(self, message):
        if message.author == self.user:
            logging.info('Message from Self')
            return
        
        elif str(message.author) == self.informio.author:
            logging.info('Message from Informio')
            return
        
        else:
            await self.cmd_matrix.handle(message)

def main():
    token = Constants.creds['jarvis']['bot']['token']
    bot = Bot(intents=discord.Intents.all())
    bot.run(token)

if __name__ == '__main__':
    main()