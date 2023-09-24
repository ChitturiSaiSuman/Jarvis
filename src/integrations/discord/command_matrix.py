from src.common.config import Constants
from src.common.trigger_loader import TriggerLoader
from src.common.util import UTIL
from src.integrations.discord.cyberparser import CyberParser


class CommandMatrix:
    def __init__(self):
        self.trigger_loader = TriggerLoader()
        self.cyber_parser = CyberParser(self.trigger_loader)