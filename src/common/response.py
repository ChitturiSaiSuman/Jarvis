#!/usr/bin/python3

import logging

from src.common import artificer, config


class Response:
    @classmethod
    def load(cls) -> dict:
        return config.Constants.response

    def __init__(self, response_type: str, response: str):
        self.raw = response
        self.__resp = self.load()
        artist = artificer.Artificer(self.__resp[response_type], self.raw)
        self.resp_type = response_type
        self.art = artist.touch()

    def __str__(self) -> str:
        return f"```ansi\n{self.art}```"
    
    def add(self, other_response, sep='\n'):
        if isinstance(other_response, Response):
            self.art += sep + other_response.art
            return self
        elif isinstance(other_response, str):
            return Response(self.resp_type, self.raw + other_response)
        else:
            raise TypeError('Unsupported operand for +')

    def __add__(self, other_response):
        if isinstance(other_response, Response):
            self.art += other_response.art
            return self
        elif isinstance(other_response, str):
            return Response(self.resp_type, self.raw + other_response)
        else:
            raise TypeError('Unsupported operand for +')