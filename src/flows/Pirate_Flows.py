#!/usr/bin/python3

import collections
import time

from src.common.Flow import Flow
from src.common.response import Response
from src.services.informio import Informio
from src.services.pirate import Pirate


class Torrent(Flow):
    """
    Handles various routines of BitTorrent
    based on the task and additional arguments.

    Trigger:
        !torrent

    Execution Args:
        task (str): {"list", "add", "remove", "start", "pause"}
        Additional Args:
            "list":
                None
            "add":
                "url": {"magnet_url", "http_url"} or
                "attachment": {"torrent_file"}
            "remove":
                "id": {"torrent_id"}
            "start":
                "id": {"torrent_id"}
            "pause":
                "id": {"torrent_id"}

    Returns:
        Response based on the task chosen. If args mismatch, a message
        representing the issue will be returned.

    Notes:
        This function requires a BitTorrent client to be installed on the system,
        such as uTorrent, qBittorrent, or Transmission.

        It is important to note that downloading copyrighted material may be illegal
        in some countries. Please ensure that you comply with the applicable laws
        and regulations of your jurisdiction.

    Example Args:
        1.
            !torrent
            task = list
        2.
            !torrent
            task = add
            url = magnet:?xt=urn:btih:c8bb8c7e50bbae9bc9599639e835c0117f0c7e3d&dn=example.torrent
        3.
            !torrent
            task = add
            url = https://<torrent_link>.torrent
        4.
            !torrent
            task = add
            # Add an attachment
        5.
            !torrent         !torrent         !torrent
            task = stop     task = start    task = pause
            id = 1          id = 2          id = 4

    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return '!torrent'

    def exec(self, args: collections.defaultdict) -> dict:
        client = Pirate()

        try:
            task = args.get('task')

            if task == 'list':
                if len(args) > 1:
                    raise ValueError('Got Invalid number of Arguments')
                resp = client.list()

            elif task == 'add':
                if 'torrent' in args or 'url' in args:
                    if len(args) > 2:
                        raise ValueError('Got Invalid number of Arguments')
                    if 'url' in args:
                        torrent = args.get('url')
                    else:
                        torrent = args.get('torrent')
                    resp = client.add(torrent)

                else:
                    raise ValueError(f'Missing argument/attachment for task {task}')

            elif task in ['remove', 'start', 'pause']:
                if 'id' not in args:
                    raise ValueError(f'Id not provided for task {task}')
                elif len(args) > 2:
                    raise ValueError('Got Invalid number of Arguments')
                else:
                    torrent_id = int(args.get('id'))
                    resp = client.__getattribute__(task)(torrent_id)

            else:
                resp = {
                    'status': 'error',
                    'message': f'Invalid task: {task}'
                }

        except Exception as e:
            resp = {
                'status': 'error',
                'message': str(e)
            }

        return resp
    
    def capture_discord(self, args: collections.defaultdict, informio: Informio):
        acknowledgement = Response('success', f'{self.trigger()} request has been captured. Please wait!')
        informio.send_message(str(acknowledgement))

        time.sleep(1)

        if 'attachment' in args:
            args['torrent'] = args['attachment']
            args.pop('attachment')

        resp = self.exec(args)

        self.respond_discord(resp, informio)


    def respond_discord(self, resp: collections.defaultdict, informio: Informio):
        
        if resp['status'] == 'success':
            response = Response('success', 'Your moment of anticipation is over. Here ya go!')
            response += Response('info', resp['message'])

        else:
            response_text = "It appears we've encountered an unexpected problem!\n"
            response_text += '\n'.join(
                [
                    f'{key}: {value}' for key, value in resp.items()
                ]
            )
            response = Response('error', response_text)

        informio.send_message(str(response))

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