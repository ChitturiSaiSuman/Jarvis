import discord_webhook
from src.common import config

class Informio:
    '''
    A tool for delivering important information or messages,
    inspired by the Latin root "informare",
    which means "to give shape to, to form, to instruct, to inform".

    Uses discord webhooks to transmit messages to specific discord channels
    '''

    def __init__(self):
        self.webhook_url = config.Constants.creds['webhooks']['#general']['informio']['url']
        self.author = config.Constants.creds['webhooks']['#general']['informio']['author']

        self.webhook = discord_webhook.DiscordWebhook(url=self.webhook_url)

    def send_message(self, text: str) -> None:
        '''
        Delivers a message to the general channel on discord
        '''
        self.webhook.content = text
        self.webhook.execute()


if __name__ == '__main__':
    informer = Informio()
    informer.send_message("Hello, World!")