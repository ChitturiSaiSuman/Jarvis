#!/usr/bin/python3

import asyncio
import logging

import discord, multiprocessing

from src.common.config import Constants
from src.integrations.discord.command_matrix import CommandMatrix
from src.services.informio import Informio
from src.services.librarian import download


class Bot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.informio = Informio()
        self.cmd_matrix = CommandMatrix()

    async def on_ready(self):
        ready_message = 'We have logged in as {0.user}'.format(self)
        logging.info(ready_message)
        print(ready_message)

    async def on_message(self, message: discord.Message):
        if message.content == 'drive':
            process = multiprocessing.Process(
                target=download
            )
            process.start()
            await message.reply('Download started')
            return
        
        if message.author == self.user:
            logging.info('Message from Self')
            return
        
        elif str(message.author) == self.informio.author:
            logging.info('Message from Informio')
            return
        
        # elif message.content.startswith('!play'):
        #     file_path = message.content.split()[1]

        #     voice_channel = message.author.voice.channel
        #     if voice_channel:
        #         try:
        #             await voice_channel.connect()
        #         except:
        #             await voice_channel.disconnect()
        #     else:
        #         await message.channel.send("You must be in a voice channel to play music.")
        #         return
            
        #     source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(file_path))

        #     # Play the source
        #     voice_channel = self.voice_clients[0]
        #     voice_channel.play(source)

        #     # while voice_channel.is_playing:
        #     #     continue

        #     # Wait until the song is finished playing
        #     # await voice_channel.wait_for("speaking")

        #     # Disconnect from the voice channel
        #     # await voice_channel.disconnect()
        
        else:
            await self.cmd_matrix.handle(message)

def main():
    token = Constants.creds['jarvis']['bot']['token']
    bot = Bot(intents=discord.Intents.all())
    bot.run(token)

if __name__ == '__main__':
    main()