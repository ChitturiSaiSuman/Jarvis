import collections
import concurrent.futures
import logging
import typing

from src.common.config import Constants
from src.common.Flow import Flow
from src.common.util import UTIL


class TriggerLoader:
    class Swift:
        class State:
            def __init__(self):
                self.next = collections.defaultdict(lambda: None)
                self.trigger = None
                self.job = None
                self.trigger_type = None

            def __str__(self):
                return '\n'.join([
                    f'Trigger: {self.trigger}',
                    f'Type: {self.trigger_type}',
                    f'Job: {self.job}'
                ])

        def __init__(self):
            self.genesis = TriggerLoader.Swift.State()
            self.tally = 0

        def load(self, trigger: str, job: typing.Callable, trigger_type: str):
            state = self.genesis
            for channel in trigger:
                if state.next[channel] == None:
                    state.next[channel] = TriggerLoader.Swift.State()
                state = state.next[channel]
            if state.job:
                logging.error(f"Cannot add Duplicate Trigger {trigger}")
                raise KeyError(f"Cannot add Duplicate Trigger {trigger}")

            state.trigger = trigger
            state.job = job
            state.trigger_type = trigger_type

            logging.info(f"{trigger}: {job} loaded")
            return f"{trigger}: {job} loaded"

        def fetch(self, trigger: str) -> State:
            state = self.genesis
            for channel in trigger:
                if state.next[channel] == None:
                    logging.error(f"Cannot find the Trigger {trigger}")
                    raise KeyError(f"Cannot find the Trigger {trigger}")
                state = state.next[channel]
            return state

        def manifest(self) -> list:
            triggers = []
            stream = collections.deque()
            state = self.genesis
            stream.append(state)
            while stream:
                state = stream.popleft()
                if state.job:
                    triggers.append(state)
                stream.extend(list(state.next.values()))
            return triggers

    def __init__(self):
        self.swift = TriggerLoader.Swift()
        self.__load_flows()
        self.__load_utils()

    def fetch(self, trigger: str) -> tuple:
        state = self.swift.fetch(trigger)
        if state.trigger_type in ['utility', 'power']:
            return state, self.messages[state.trigger]
        return state, None
    
    def manifest(self) -> list:
        return self.swift.manifest()

    def __load_flows(self):
        flows = Flow.discover_descendants()
        flows = [[flow.trigger(), flow, 'flow'] for flow in flows]

        def async_load(item):
            return self.swift.load(*item)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(async_load, flows))

    def __load_utils(self):
        utils = Constants.util
        
        utility = {
            key: utils['utility'][key] for key in utils['utility']
        }

        power = {
            key: utils['power'][key] for key in utils['power']
        }

        utility_routines = [
            [
                key, self.__get_util(utility[key]['callable']), 'utility'
            ]
            for key in utility
        ]

        power_routines = [
            [
                key, self.__get_util(power[key]['callable']), 'power'
            ]
            for key in power
        ]

        def async_load(item):
            return self.swift.load(*item)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            list(executor.map(async_load, utility_routines + power_routines))

        self.messages = {
            triplet[0]: utils[triplet[2]][triplet[0]]['message']
            for triplet in utility_routines + power_routines
        }

        self.utils = self.messages.keys()

    def __get_util(self, routine: str) -> typing.Callable:
        if hasattr(UTIL, routine):
            routine = getattr(UTIL, routine)
            if not callable(routine):
                raise ValueError(f"Routine {routine} in {UTIL} not callable")
            return routine
        else:
            raise ValueError(f"Routine {routine} not found in {UTIL}")

if __name__ == '__main__':
    TriggerLoader()