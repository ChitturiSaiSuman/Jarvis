#!/usr/bin/python3

import collections
import importlib
import inspect
import logging
import os
import textwrap
from abc import ABC, abstractmethod

import discord

import src.flows
from src.services.informio import Informio


class Flow(ABC):
    """
    Base class for defining a flow structure.

    This class provides a virtual structure for a flow and requires subclasses
    to implement the abstract methods defined here.

    Subclasses inheriting from this class must implement the following abstract methods:
        - trigger(): Shows the method execution trigger (typically a !message for discord)
        - exec(): Execute the main logic of the flow.
        - ps(): Shows the current status of the flow.
        - purge(): Perform any necessary cleanup after the flow has finished.
    """

    @classmethod
    def whoami(cls) -> str:
        """
        Abstract method to return a descriptive string for the child class.

        This method should be implemented by subclasses to return a descriptive string
        specific to the child class.

        Returns:
            str: A descriptive string for the child class.
        """
        return textwrap.dedent(cls.__doc__)

    @classmethod
    @abstractmethod
    def trigger(cls) -> str:
        """
        Method that returns the trigger string,
        a string that should be used as a prefix to
        initiate the flow

        Returns:
            str: A prefix string for the child class.
        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass

    @abstractmethod
    def exec(self, args: collections.defaultdict) -> dict:
        """
        Abstract method to execute the main logic for the flow.

        This method should be implemented by subclasses to define and execute
        the main logic of the flow.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass

    @abstractmethod
    async def capture_discord(self, args: collections.defaultdict, message: discord.Message, informio: Informio):
        """
        Abstract method to capture flow request in Discord. The method
        can make use of the 'message' argument and the 'informio' argument
        to capture attachments and use them for sending appropriate responses

        This method should be implemented by subclasses to enable flows
        to capture metadata from the 'message' argument.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass

    @abstractmethod
    async def __respond_discord(self, args: collections.defaultdict, message: discord.Message, informio: Informio):
        """
        Abstract method to prepare the response in discord. The method
        can make use of the 'message' argument and the 'informio' argument
        to send different types of responses

        This method should be implemented by subclasses to enable flows
        to send responses to discord channel.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass

    @classmethod
    @abstractmethod
    def ps(cls) -> list:
        """
        Abstract method to show the current status of the flow.

        This method should be implemented by subclasses to display the current
        status information of the flow.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass

    @classmethod
    @abstractmethod
    def purge(cls) -> bool:
        """
        Abstract method to perform any necessary clean-up after the flow has finished.

        This method should be implemented by subclasses to perform any necessary
        clean-up steps required after the flow has finished executing.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
        pass

    @classmethod
    def discover_descendants(cls) -> list:
        package = src.flows.__package__
        is_module = lambda module: module.endswith('.py')
        modules = filter(is_module, os.listdir(package.replace('.', '/')))
        modules = map(lambda module: module.replace('.py', ''), modules)

        descendants = []

        for module in modules:
            module = f'{package}.{module}'
            try:
                module = importlib.import_module(module)
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, cls) and obj != cls:
                        descendants.append(obj)

                logging.info(f"Imported module: {module}")
            except ImportError as e:
                logging.error(f"Failed to import module {module}: {str(e)}")

        return descendants

if __name__ == '__main__':
    print(Flow.discover_descendants())