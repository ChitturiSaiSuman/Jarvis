#!/usr/bin/python3

import collections
import json
import re
import traceback

from src.common.trigger_loader import TriggerLoader


class CyberParser:

    def __init__(self, trigger_loader: TriggerLoader):
        self.utils = set(trigger_loader.utils)
        
    def parse(self, message: str) -> dict:
        message = message.strip()
        signature = dict()

        if not message:
            signature['kind'] = 'empty'
            signature['message'] = 'Got an Empty Message'

        elif message in self.utils:
            signature['kind'] = 'util'
            signature['command'] = message
        
        elif message.startswith('!'):
            signature = self.__parse_flow_request(message)
            
        else:
            signature['kind'] = 'general'
            signature['message'] = message

        return signature

    def __parse_flow_request(self, message: str) -> dict:
        command, content = re.split(r'\s+', message.strip(), 1)
        signature = dict()

        try:

            if content.startswith('{') and content.endswith('}'):
                try:
                    json_body = json.loads(content)
                    signature['king'] = 'flow'
                    signature['command'] = command
                    signature['args'] = json_body
                
                except json.JSONDecodeError as e:
                    signature['kind'] = 'error'
                    signature['message'] = traceback.format_exc()
                    
            else:
                content_lines = content.splitlines()
                pairs = []
                for line in content_lines:
                    match = re.match(r'(\w+)\s*[:=]\s*(.*)', line)
                    if match:
                        key, value = match.groups()
                        value = json.loads(f"[{value}]")[0]
                        pairs.append((key, value))
                    else:
                        pairs = []
                        break

                if pairs:
                    body = collections.defaultdict(lambda: None, dict(pairs))
                    signature['kind'] = 'flow'
                    signature['command'] = command
                    signature['args'] = body
                
                else:
                    signature['kind'] = 'error'
                    signature['message'] = 'Unable to decode pairs'

        except Exception as e:
            signature['kind'] = 'error'
            signature['message'] = traceback.format_exc()

        return signature