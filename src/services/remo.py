#!/usr/bin/python3

import asyncio
import collections
import inspect
import json
import logging

from src.common import config
from src.services.executor import Executor
from src.services.job import Job


class Remo:
    @classmethod
    def __is_executor(cls, member) -> bool:
        return inspect.isclass(member[1]) and member[1].__module__ == Executor.__module__

    @classmethod
    def __list_executors(cls) -> list:
        return list(filter(cls.__is_executor, inspect.getmembers(Executor)))

    @classmethod
    def __load(cls) -> dict:
        cls.__executors = dict(cls.__list_executors())

    def __init__(self, args: collections.defaultdict):
        Remo.__load()

        if args['lang'] not in Remo.__executors:
            error_message = f"Unidentified Language: {args['lang']}"
            raise ValueError(error_message)

        self.lang = args['lang']
        self.args = args

    def run(self) -> collections.defaultdict:
        response = collections.defaultdict()
        try:
            executor = Remo.__executors[self.lang]()

            prep_response = executor.prepare(self.args)
            if prep_response['status'] == 'error':
                return prep_response
            
            run_response = executor.run()
            return run_response
        
        except Exception as e:
            response['status'] = 'error'
            response['message'] = str(e)
            
        return response



async def async_function(executor: Job, args, last_function):
    print(executor.start(args))
    last_function()

def main():
    # cpp_executor = executor.Executor.CPP()
    # source = open('/home/suman/Jarvis/src/services/test.cpp', 'r').read()
    source = "print('hello awesome')\nprint('awesome guy entered: ', int(input()))"

    stdin = "7"

    args = {
        'lang': 'PYTHON',
        'path': '/home/suman/Desktop/',
        'source': source,
        'source_file_name': 'Test.py',
        'stdin': stdin
    }

    # def some_function():
    #     print("Inside some_function")

    # asyncio.create_task(async_function(cpp_executor, args, some_function))
    # print("This should be printed immediately")

    rse_obj = Remo(args)
    print(json.dumps(rse_obj.run(), indent=4))

    # source = open('test/code.c', 'r').read()
    # stdin = open('stdin', 'r').read()

    # args = {
    #     'lang': 'C',
    #     'path': '/home/suman/Desktop/',
    #     'source': source,
    #     'source_file_name': 'Test.cpp',
    #     'time_limit': 10,
    #     'memory_limit': 10**6,
    #     'stdin': stdin
    # }

    # rse_obj = Remo(args)
    # print(json.dumps(rse_obj.run(), indent=4))