#!/usr/bin/python3

from src.common.config import Constants
from src.common.response import Response
from src.common.trigger_loader import TriggerLoader
import src.integrations.discord.bot as bot
from src.services.informio import Informio


def __send_welcome():

    greeting = Constants.setup['greeting']
    comment = Constants.setup['comment']

    trigger_loader = TriggerLoader()
    
    triggers = Constants.util['utility'].keys()

    states_and_messages = list(map(trigger_loader.fetch, triggers))

    information_for_user = '\n'.join([
        f'{message}{state.job()}' for state, message in states_and_messages
    ])

    welcome_message = Response('success', greeting + '\n')
    welcome_message += Response('info', comment + '\n')
    welcome_message += Response('general', information_for_user)

    Informio().send_message(str(welcome_message))

def start():
    __send_welcome()
    bot.main()