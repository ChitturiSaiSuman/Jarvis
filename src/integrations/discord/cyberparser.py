import collections
import json
import re

from src.common.trigger_loader import TriggerLoader


class CyberParser:
    class Message:
        def __init__(self):
            pass

    def __init__(self, trigger_loader: TriggerLoader):
        self.utils = set(trigger_loader.utils)
        

    def parse(self, message: str) -> Message:
        message = message.strip()
        if not message:
            # TODO
            signature = CyberParser.Message()
            signature.kind = 'empty'
            return signature

        if message in self.utils:
            signature = CyberParser.Message()
            signature.kind = 'util'
            signature.command = message
        
        elif message.startswith('!'):
            signature = self.__parse_flow_request(message)
            
        else:
            signature = CyberParser.Message()
            signature.kind = 'general'
            signature.message = message
            

    def __parse_flow_request(self, message: str):
        command, content = re.split(r'\s+', message.strip(), 1)
        if content.startswith('{') and content.endswith('}'):
            try:
                json_body = json.loads(content)
                signature = CyberParser.Message()
                signature.kind = 'flow'
                signature.command = command
                signature.args = json_body
                return signature
            
            except json.JSONDecodeError as e:
                signature = CyberParser.Message()
                signature.kind = 'error'
                signature.message = str(e)
                return signature
        else:
            pairs = re.findall(r'(\w+)\s*[:=]\s*([^=\n]+)', content)
            if pairs:
                body = collections.defaultdict(pairs)
                signature = CyberParser.Message()
                signature.kind = 'flow'
                signature.command = command
                signature.args = body
                return signature
            
            else:
                signature = CyberParser.Message()
                signature.kind = 'error'
                signature.message = 'Unable to decode pairs'