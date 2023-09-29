#!/usr/bin/python3

import collections
import io
import logging
import time

import discord

from src.common.Flow import Flow
from src.common.response import Response
from src.services.informio import Informio
from src.services.remo import Remo


class RemoteScriptExecution(Flow):
    """
    Executes Scripts remotely on the Target machine

    Trigger:
        !rse

    Execution Args:
        lang (str): The Language of the Script
        source (str): The source code of the Script
        time_limit (int): Time limit for the Job in seconds
        memory_limit (int): Memory limit for the Job in Kilobytes
        stdin (str): Standard input (Empty String for No input)
        source_file_name (str): Name of the file to which source has to be written (Not required if lang in C, CPP, PYTHON)
        path (str): Target location for Execution

    Raises:
        ValueError: If any of the Args are not provided

    Notes:
        This Utility requires the Languages pre-installed on the machine.

        It is important to note that the actions performed by the scripts
        are not restricted or controlled. Be careful while performing
        any admin actions that may involve data loss or corruption.

    Example args: {
        "lang": "PYTHON",
        "source: "import os\nprint(os.listdir())",
        "time_limit": 2,
        "memory_limit": 10240,
        "stdin": "",
        "path": "/home/suman/"
    }
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return '!rse'

    def exec(self, args: collections.defaultdict) -> dict:
        try:
            rse_obj = Remo(args)
            response = rse_obj.run()
            self.traces.append(response)
            return response
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        
    async def capture_discord(self, args: collections.defaultdict, message: discord.Message, informio: Informio):
        acknowledgement = Response('success', f'{self.trigger()} request has been captured. Please wait!')
        informio.send_message(str(acknowledgement))

        time.sleep(1)

        if message.attachments:
            attachment = await message.attachments[0].read()
            attachment = attachment.decode()
            args['source'] = attachment
        
        resp = self.exec(args)

        await self.respond_discord(resp, message, informio)

    async def respond_discord(self, resp: collections.defaultdict, message: discord.Message, informio: Informio):
        
        if resp['status'] == 'success':
            stdout_file = discord.File(io.BytesIO(resp['stdout'].encode()), filename="stdout")
            stderr_file = discord.File(io.BytesIO(resp['stderr'].encode()), filename="stderr")
            files_to_upload = [stdout_file, stderr_file]
            response = Response('success', 'Your moment of anticipation is over. Here ya go!')

            await message.reply(str(response), files = files_to_upload)

        else:
            response_text = "It appears we've encountered an unexpected problem!\n"
            response_text += '\n'.join(
                [
                    f'{key}: {value}' for key, value in resp.items()
                ]
            )
            response = Response('error', response_text)
            await message.reply(str(response))

    @classmethod
    def ps(cls) -> list:
        return cls.traces

    @classmethod
    def purge(cls) -> bool:
        try:
            cls.traces.clear()
            return True
        except:
            return False