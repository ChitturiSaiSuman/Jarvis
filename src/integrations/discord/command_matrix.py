#!/usr/bin/python3

import logging

import discord

from src.common.response import Response
from src.common.trigger_loader import TriggerLoader
from src.integrations.discord.cyberparser import CyberParser
from src.services.informio import Informio


class CommandMatrix:
    def __init__(self):
        self.trigger_loader = TriggerLoader()
        self.cyber_parser = CyberParser(self.trigger_loader)
        self.informio = Informio()

    async def handle(self, message: discord.Message):
        content = message.content
        signature = self.cyber_parser.parse(content)

        if signature['kind'] == 'empty':
            response = Response('warning', signature['message'])
            await message.reply(response)
        
        elif signature['kind'] == 'error':
            response = Response('error', signature['message'])
            await message.reply(str(response))

        else:
            if signature['kind'] == 'general':
                ping_from_user = signature['message']
                # TODO
                # Implement a ChatBot that will have the context of
                # previous general messages and responds accordingly
                response = Response('general', f'Got message {ping_from_user}')
                self.informio.send_message(str(response))

            elif signature['kind'] == 'util':
                state, routine_message = self.trigger_loader.fetch(signature['command'])

                if state.trigger_type == 'power':
                    response = Response('warning', routine_message)
                    await message.reply(str(response))
                    state.job()
                
                else:
                    assert state.trigger_type == 'utility'
                    routine_message += state.job()
                    response = Response('info', routine_message)
                    await message.reply(str(response))

            else:
                assert signature['kind'] == 'flow'
                command = signature['command']
                args = signature['args']
                
                state, _ = self.trigger_loader.fetch(command)
                await state.job().capture_discord(args, message, self.informio)