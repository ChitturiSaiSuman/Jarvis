import collections
from src.common.Flow import Flow
from src.services.remo import Remo

class RemoteScriptExecution(Flow):
    """
    Executes Scripts remotely on the Target machine

    Trigger:
        !rse

    Execution Args:
        lang (str): The Language of the Script
        source (str): The source code of the Script
        time_limit (int): Time limit for the Job in seconds
        memory_limit (int): Memory limit for the Job in Kilobytes
        stdin (str): Standard input (Empty String for No input)
        source_file (str): Name of the file to which source has to be written (Not required if lang in C, CPP, PYTHON)
        path (str): Target location for Execution

    Raises:
        ValueError: If any of the Args are not provided

    Notes:
        This Utility requires the Languages pre-installed on the machine.

        It is important to note that the actions performed by the scripts
        are not restricted or controlled. Be careful while performing
        any admin actions that may involve data loss or corruption.

    Example args: {
        "lang": "PYTHON",
        "source: "import os\nprint(os.listdir())",
        "time_limit": 2,
        "memory_limit": 10240,
        "stdin": "",
        "path": "/home/suman/"
    }
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return '!rse'
    
    def exec(self, args: collections.defaultdict) -> dict:
        try:
            rse_obj = Remo(args)
            response = rse_obj.run()
            self.traces.append(response)
            return {
                'response': response
            }
        except Exception as e:
            return {
                'response': str(e)
            }
    
    @classmethod
    def ps(cls) -> list:
        return cls.traces
    
    @classmethod
    def purge(cls) -> bool:
        try:
            cls.traces.clear()
            return True
        except:
            return False