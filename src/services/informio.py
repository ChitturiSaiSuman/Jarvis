#!/usr/bin/python3


import discord_webhook
import os

from src.common.config import Constants


class Informio:
    """
    A tool for delivering important information or messages,
    inspired by the Latin root "informare",
    which means "to give shape to, to form, to instruct, to inform".

    Uses discord webhooks to transmit messages to specific discord channels
    """

    def __init__(self):
        self.webhook_url = Constants.creds["webhooks"]["#general"][
            "informio"
        ]["url"]
        self.author = Constants.creds["webhooks"]["#general"][
            "informio"
        ]["author"]

        self.webhook = discord_webhook.DiscordWebhook(
            url=self.webhook_url
        )

    def send_message(self, text: str, files: list) -> None:
        """
        Delivers a message to the general channel on discord
        """
        self.webhook.content = text

        for file_path in files:
            with open(file_path, "rb") as file:
                self.webhook.add_file(
                    file=file.read(),
                    filename=os.path.basename(file_path),
                )

        self.webhook.execute()


if __name__ == "__main__":
    informer = Informio()
    informer.send_message("Hello, World!")
