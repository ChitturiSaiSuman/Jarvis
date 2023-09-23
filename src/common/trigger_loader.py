import typing, collections, concurrent.futures
from src.common.Flow import Flow

class TriggerLoader:
    class Swift:
        class State:
            def __init__(self):
                self.next = collections.defaultdict(lambda: None)
                self.trigger = None
                self.job = None

        def __init__(self):
            self.genesis = TriggerLoader.Swift.State()
            self.tally = 0

        def load(self, trigger: str, job: typing.Callable):
            state = self.genesis
            for channel in trigger:
                if state.next[channel] == None:
                    state.next[channel] = TriggerLoader.Swift.State()
                state = state.next[channel]
            if state.job:
                raise KeyError(f"Cannot add Duplicate Trigger {trigger}")

            state.trigger = trigger
            state.job = job

            return f"{trigger}: {job} loaded"

        def fetch(self, trigger: str) -> typing.Callable:
            state = self.genesis
            for channel in trigger:
                if state.next[channel] == None:
                    raise KeyError(f"Cannot find the Trigger {trigger}")
                state = state.next[channel]
            return state.job

        def manifest(self) -> list:
            triggers = []
            stream = collections.deque()
            state = self.genesis
            stream.append(state)
            while stream:
                state = stream.popleft()
                if state.job:
                    triggers.append((state.trigger, state.job))
                stream.extend(list(state.next.values()))
            return triggers

    def __init__(self):
        loader = TriggerLoader.Swift()
        flows = Flow.discover_descendants()
        flows = [[flow.trigger(), flow] for flow in flows]

        def async_load(item):
            return loader.load(*item)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(async_load, flows))

        print(results)
        print(loader.manifest())


if __name__ == '__main__':
    TriggerLoader()