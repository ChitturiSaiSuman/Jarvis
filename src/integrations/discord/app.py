#!/usr/bin/python3

import functools

import src.integrations.discord.bot as bot
from src.common.config import Constants
from src.common.response import Response
from src.common.trigger_loader import TriggerLoader
from src.services.informio import Informio


def __send_welcome():

    greeting = Constants.setup['greeting']
    comment = Constants.setup['comment']

    trigger_loader = TriggerLoader()
    
    triggers = Constants.util['utility'].keys()

    states_and_messages = list(map(trigger_loader.fetch, triggers))

    responses = [
        (message, state.job()) for state, message in states_and_messages
    ]

    responses = map(
        lambda response: (
            response[0],
            'error' if response[1]['status'] == 'error' else 'general',
            response[1]['message']
        ),
        responses
    )

    status = functools.reduce(
        lambda resp1, resp2: resp1.add(resp2),
        [Response('general', triplet[0]) + Response(triplet[1], str(triplet[2])) for triplet in responses]
    )

    print(status)

    welcome_message = Response('success', greeting + '\n')
    welcome_message += Response('info', comment + '\n')

    welcome_message += status

    Informio().send_message(str(welcome_message))

def start():
    __send_welcome()
    bot.main()