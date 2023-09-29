#!/usr/bin/python3

import collections
import re
import logging

from src.common.config import Constants


class Artificer:
    @classmethod
    def load(cls) -> dict:
        return Constants.chroma

    def __construct(self, text: str):
        self.nOiCe= f"\u001b[{self.format};{self.bg_color};{self.fg_color}m{text}\u001b[0;0m"
        self.nOiCe = re.sub(r';+', ';', self.nOiCe)

    def __set_format(self, args: collections.defaultdict):
        defaults = self.chroma['default']
        self.format = args.get('format', defaults['format'])
        self.format = list(map(self.chroma['format'].get, self.format))
        self.format = list(map(str, sorted(self.format)))
        self.format = ';'.join(self.format)

    def __set_bg_color(self, args: collections.defaultdict):
        defaults = self.chroma['default']
        self.bg_color = args.get('background-color', defaults['background-color'])
        if self.bg_color != "":
            self.bg_color = self.chroma['background-color'][self.bg_color]

    def __set_fg_color(self, args: collections.defaultdict):
        defaults = self.chroma['default']
        self.fg_color = args.get('foreground-color', defaults['foreground-color'])
        if self.fg_color != "":
            self.fg_color = self.chroma['foreground-color'][self.fg_color]

    def __set_attrs(self, args: collections.defaultdict) -> bool:
        self.__set_format(args)
        self.__set_bg_color(args)
        self.__set_fg_color(args)

    def __init__(self, setup: collections.defaultdict, text: str):
        self.chroma = self.load()
        self.__set_attrs(setup)
        self.__construct(text)

    def touch(self) -> str:
        return self.nOiCe