#!/usr/bin/python3

from src.integrations.discord import app as discord_app
import logging
from src.common.config import Constants

class Jarvis:
    def __init__(self):
        pass

if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.INFO,
        filename=Constants.setup['log'],
        filemode='w'
    )
    discord_app.start()