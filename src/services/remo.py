from src.common import config
from src.services.job import Job
from src.services.executor import Executor
import asyncio, collections, inspect, json

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
            raise ValueError("Unidentified Executor: ", args['lang'], sep='')
        self.lang = args['lang']
        self.args = args

    def run(self) -> collections.defaultdict:
        response = collections.defaultdict()
        try:
            self.executor = Remo.__executors[self.lang]()
            self.prep_response = self.executor.prepare(self.args)
            self.run_response = self.executor.run()
            response['dump'] = self.prep_response, self.run_response
        except Exception as e:
            response['error'] = str(e)
        return response



async def async_function(executor: Job, args, last_function):
    print(executor.start(args))
    last_function()

async def main():
    # cpp_executor = executor.Executor.CPP()
    source = open('test/code.cpp', 'r').read()
    stdin = open('stdin', 'r').read()

    args = {
        'lang': 'CPP',
        'path': '/home/suman/Desktop/',
        'source': source,
        'source_file_name': 'Test.cpp',
        'time_limit': 10,
        'memory_limit': 10**6,
        'stdin': stdin
    }

    # def some_function():
    #     print("Inside some_function")

    # asyncio.create_task(async_function(cpp_executor, args, some_function))
    # print("This should be printed immediately")

    rse_obj = Remo(args)
    print(json.dumps(rse_obj.run(), indent=4))

    source = open('test/code.c', 'r').read()
    stdin = open('stdin', 'r').read()

    args = {
        'lang': 'C',
        'path': '/home/suman/Desktop/',
        'source': source,
        'source_file_name': 'Test.cpp',
        'time_limit': 10,
        'memory_limit': 10**6,
        'stdin': stdin
    }

    rse_obj = Remo(args)
    print(json.dumps(rse_obj.run(), indent=4))