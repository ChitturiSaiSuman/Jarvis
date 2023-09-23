import collections

from src.common.Flow import Flow
from src.services.pirate import Pirate


class MagnetDownload(Flow):
    """
    Downloads a torrent file from a magnet URL.

    Trigger:
        !magnet

    Execution Args:
        magnet_url (str): The magnet URL of the torrent to download.

    Returns:
        bool: True if the torrent was successfully downloaded, False otherwise.

    Raises:
        ValueError: If the magnet URL is invalid or empty.

    Notes:
        This function requires a BitTorrent client to be installed on the system,
        such as uTorrent, qBittorrent, or Transmission.

        It is important to note that downloading copyrighted material may be illegal
        in some countries. Please ensure that you comply with the applicable laws
        and regulations of your jurisdiction.

    Example magnet url: "magnet:?xt=urn:btih:c8bb8c7e50bbae9bc9599639e835c0117f0c7e3d&dn=example.torrent"
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return '!magnet'

    def exec(self, args: collections.defaultdict) -> dict:
        magnet_url = args.get('magnet_url')
        client = Pirate()
        response = client.add(magnet_url)
        self.traces.append(response)
        return {
            'response': response
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


class TorrentFromHTTP(Flow):
    """
    Downloads a torrent file from a HTTP URL.

    Trigger:
        !torrent_http

    Execution Args:
        torrent_url (str): The HTTP URL pointing to the torrent file.

    Returns:
        bool: True if the torrent was successfully downloaded, False otherwise.

    Raises:
        ValueError: If the URL is invalid or empty.

    Notes:
        This function requires a BitTorrent client to be installed on the system,
        such as uTorrent, qBittorrent, or Transmission.

        It is important to note that downloading copyrighted material may be illegal
        in some countries. Please ensure that you comply with the applicable laws
        and regulations of your jurisdiction.

    Example URL: "http://example.com/example.torrent"
    """

    traces = []

    @classmethod
    def trigger(cls) -> str:
        return '!torrent_http'

    def exec(self, args: collections.defaultdict) -> dict:
        url = args.get('torrent_url')
        client = Pirate()
        response = client.add(url)
        self.traces.append(response)
        return {
            'response': response
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