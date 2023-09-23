import collections, json, time, transmission_rpc, typing, os

class Pirate:
    '''
    Pirate is a Torrent Handler built on
    transmission_rpc, which is a popular
    torrent client for Ubuntu server
    '''
    class TorrentInfo:
        '''
        A class to store information of a torrent.
        '''
        def __init__(self, torrent: transmission_rpc.torrent.Torrent) -> None:
            self.torrent = torrent

        def get_info(self) -> str:
            '''
            Returns information of a torrent.
            '''
            torrent = self.torrent
            try:
                info = collections.OrderedDict({
                    'ID': torrent.id,
                    'Name': torrent.name,
                    'Status': torrent.status,
                    'Progress': torrent.progress,
                    'Download Speed': torrent.rate_download / 10**6,
                    'Upload Speed': torrent.rate_upload / 10**6,
                    'Seeders': torrent.peers_connected,
                    'ETA': None,
                    'Total Size': round(torrent.total_size / 10**6),
                    'Error': torrent.error,
                    'Error String': torrent.error_string,
                    'ETA': torrent.eta
                })
                return json.dumps(info, indent=4, default=str)
            except Exception as e:
                alternate_message = f'An error Occured: {e}'
                return alternate_message

        def __str__(self) -> str:
            try:
                return self.get_info()
            except Exception as e:
                alternate_message = f'An error Occured: {e}'
                return alternate_message

        def __repr__(self) -> str:
            try:
                return self.__str__()
            except Exception as e:
                alternate_message = f'An error Occured: {e}'
                return alternate_message

    def __init__(self, host='localhost', port=9091, username='transmission', password='transmission'):
        self.client = transmission_rpc.Client(host=host, port=port, username=username, password=password)

    def list(self) -> str:
        '''
        Returns info of all active torrents.
        '''
        try:
            torrents = self.client.get_torrents()
            if torrents == []:
                return 'No torrents found!'
            return '\n'.join(list(map(str, map(Pirate.TorrentInfo, torrents))))
        except Exception as e:
            alternate_message = f'An error Occured: {e}'
            return alternate_message

    def add(self, torrent: typing.Union[str, bytes]) -> str:
        '''
        Adds a torrent to the download queue and begins downloading it.

        Args:
            torrent: One of the following
                1. str object representing a magnet URL or an http(s) URL
                2. str object representing the path to a Torrent file
                3. bytes object representing torrent info

        Returns:
            str object representing the response.
        '''
        response = []

        if isinstance(torrent, str):
            if torrent.startswith('magnet'):
                response.append('Adding torrent from magnet URL...')
            elif torrent.startswith('http'):
                response.append('Adding torrent from HTTP URL...')
            elif os.path.exists(torrent):
                response.append('Adding torrent from file...')

        elif isinstance(torrent, bytes):
            response.append('Adding torrent from torrent file data...')

        else:
            response.append('Could not add torrent. Received invalid arguments.')
            return response

        try:
            torrent = self.client.add_torrent(torrent)
            response.append(f"Torrent {torrent.name} added")

        except transmission_rpc.TransmissionError as e:
            message = f'Failed to add torrent. Message: {e}'
            response.append(message)

        return '\n'.join(response)

    def remove(self, id: int, delete_data=False) -> str:
        '''
        Removes torrent with provided id. Local data is deleted if delete_data is True.
        '''
        response = []
        try:
            self.client.remove_torrent(id, delete_data=delete_data)
            response.append(f'Removed torrent with id {id} successfully')
        except Exception as e:
            response.append(f'Failed to remove torrent. Message: {e}')

        return '\n'.join(response)

    def start(self, id: int) -> str:
        '''
        Starts torrent with provided id.
        '''
        response = []
        try:
            self.client.start_torrent(id)
            response.append(f'Started torrent with id {id} successfully')
        except Exception as e:
            response.append(f'Failed to stop torrent. Message: {e}')

        return '\n'.join(response)

    def pause(self, id: int) -> str:
        '''
        Pauses torrent with provided id.
        '''
        response = []
        try:
            self.client.stop_torrent(id)
            response.append(f'Stopped torrent with id {id} successfully')
        except Exception as e:
            response.append(f'Failed to stop torrent. Message: {e}')

        return '\n'.join(response)


if __name__ == '__main__':
    torrent_handler = Pirate()
    print(torrent_handler.list())
    # print(torrent_handler.start(1))
    # print(torrent_handler.remove(1, delete_data=True))