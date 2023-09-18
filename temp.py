# from src.services import remo
# import asyncio

import logging

from src.common.trigger_loader import TriggerLoader

logging.basicConfig(level=logging.INFO, filemode='w', filename='logging.out')

TriggerLoader()

# asyncio.run(remo.main())

# import asyncio

# def some_fun():
#     print("Some fun is called")

