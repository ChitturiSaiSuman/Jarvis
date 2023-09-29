#!/usr/bin/python3

import collections
import logging
import os
import time

import discord

from src.common.Flow import Flow
from src.services.informio import Informio
from src.services.librarian import Librarian
from src.common.response import Response

class FileLocator(Flow):
    """
    Locates a File in the Local (Secondary) Storage

    Trigger:
        !locate

    Execution Args:
        path (str): Directory to search in
        pattern (str): String to match
        domain (str): Either "title" or "content"

    Raises:
        ValueError: If any of the Args are not provided

    Notes:
        "path" must be a valid path.

    Example args: {
        "path": "/home/suman",
        "pattern": "Example.txt",
        "domain": "title"
    }
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return '!locate'

    def exec(self, args: collections.defaultdict) -> dict:
        try:
            path_to_search = args.get('path')
            string_to_match = args.get('pattern')
            domain = args.get('domain')

            if domain not in ['title', 'content']:
                raise ValueError('Invalid value for domain. domain must be in ["title", "content"]')

            lib = Librarian()

            if domain == 'title':
                response = lib.title_tracker(path_to_search, string_to_match)
            else:
                response = lib.content_curator(path_to_search, string_to_match)

            if response['status'] == 'error':
                return response
            
            files = response.get('filepaths')

            self.traces.append(files)

            return {
                'status': 'success',
                'files': files
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
        
    async def capture_discord(self, args: collections.defaultdict, message: discord.Message, informio: Informio):
        acknowledgement = Response('success', f'{self.trigger()} request has been captured. Please wait!')
        informio.send_message(str(acknowledgement))

        time.sleep(1)

        resp = self.exec(args)

        await self.respond_discord(resp, message, informio)

    async def respond_discord(self, resp: collections.defaultdict, message: discord.Message, informio: Informio):
        
        if resp['status'] == 'success':
            files = resp['files']
            if files == []:
                response = Response('info', 'No file found')
            else:
                response = Response('success', 'Your moment of anticipation is over. Here ya go!')
                response += Response('info', 'Files found:')
                response += Response('general', '\n'.join(files))

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

class FileUploader(Flow):
    """
    Uploads a File to Google Drive Storage using API

    Trigger:
        !upload:

    Execution Args:
        path (str): The path to the file or folder to be uploaded
        compress (bool) [True/False]: Whether to compress the file in a Zip
        password (str) [Optional]: Password to protect the zip

    Notes:
        "path" must be a valid path.
        If "path" points to a valid directory, the directory will be automatically zipped irrespective of the compress option.
        If "path" points to a valid file, "compress" will decide whether the file should be zipped or not.
        "password", if provided, must not contain spaces.

    Example args:
    Example 1: {
        "path": "/home/suman/Jarvis",
        "compress": false, # Not considered since Jarvis is a directory
        "password": "hello"
    }
    Example 2: {
        "path": "/home/suman/Music/Sample.mp3",
        "compress": false
    }
    Example 3: {
        "path": "/home/suman/Documents",
        "compress": true
        # If password is not provided, directory will not be encrypted
    }
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return "!upload"

    def exec(self, args: collections.defaultdict) -> dict:
        try:
            file_path = args.get('path')
            compress = os.path.isdir(file_path) or args.get('compress')
            lib = Librarian()
            if compress:
                password = args.get('password', None)
                file_path = lib.archive_creator(file_path, password)

            fields = lib.tome_transporter(file_path)

            self.traces.append(file_path)
            return {
                'response': fields
            }

        except Exception as e:
            return {
                'exception': str(e)
            }
        
    async def capture_discord(self, args: collections.defaultdict, message: discord.Message, informio: Informio):
        pass

    async def respond_discord(self, args: collections.defaultdict, message: discord.Message, informio: Informio):
        pass

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