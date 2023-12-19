#!/usr/bin/python3

import collections
import os
import typing

from src.common.config import Constants

import transmission_rpc


class Pirate:
    """
    Pirate is a Torrent Handler built on
    transmission_rpc, which is a popular
    torrent client for Ubuntu server
    """

    class TorrentInfo:
        """
        A class to store information of a torrent.
        """

        def __init__(self, torrent: transmission_rpc.torrent.Torrent):
            self.torrent = torrent

        def get_info(self) -> dict:
            """
            Returns information of a torrent.
            """
            torrent = self.torrent
            try:
                info = collections.OrderedDict(
                    {
                        "ID": torrent.id,
                        "Name": torrent.name,
                        "Status": torrent.status,
                        "Progress": torrent.progress,
                        "Download Speed (KB/s)": torrent.rate_download / 1024,
                        "Upload Speed (KB/s)": torrent.rate_upload / 1024,
                        "Seeders": torrent.peers_connected,
                        "Total Size (MB)": round(torrent.total_size / 10**6),
                        "Error": torrent.error,
                        "Error String": torrent.error_string,
                        "ETA": torrent.eta,
                    }
                )

                return {"status": "success", "info": info}

            except Exception as e:
                return {"status": "error", "message": str(e)}

        def __str__(self) -> str:
            response = self.get_info()
            if response["status"] == "error":
                return response["message"]

            return "\n".join(
                [f"{key}: {value}" for key, value in response["info"].items()]
            )

        def __repr__(self) -> str:
            return self.__str__()

    def __init__(self):
        host = Constants.pirate["host"]
        port = Constants.pirate["port"]
        username = Constants.pirate["username"]
        password = Constants.pirate["password"]
        self.client = transmission_rpc.Client(
            host=host, port=port, username=username, password=password
        )

    def list(self) -> dict:
        """
        Returns info of all active torrents.
        """
        try:
            torrents = self.client.get_torrents()
            sep = "\n" + "*" * 64 + "\n"
            torrents = sep.join(list(map(str, map(Pirate.TorrentInfo, torrents))))

            return {"status": "success", "message": torrents}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def add(self, torrent: typing.Union[str, bytes]) -> dict:
        """
        Adds a torrent to the download queue and begins downloading it.

        Args:
            torrent: One of the following
                1. str object representing a magnet URL or an http(s) URL
                2. str object representing the path to a Torrent file
                3. bytes object representing torrent info

        Returns:
            dict object representing the response.
        """

        message = ""

        if isinstance(torrent, str):
            if torrent.startswith("magnet"):
                message = "Adding torrent from magnet URL..."

            elif torrent.startswith("http"):
                message = "Adding torrent from HTTP URL..."

            elif os.path.exists(torrent):
                message = "Adding torrent from file..."

            else:
                message = "Could not add torrent. Received invalid arguments."

        elif isinstance(torrent, bytes):
            message = "Adding torrent from torrent file data..."

        else:
            message = "Could not add torrent. Received invalid arguments."

        try:
            torrent = self.client.add_torrent(torrent)
            ack = f"Torrent {torrent.name} added Successfully!"
            return {"status": "success", "message": message + "\n" + ack}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def remove(self, id: int, delete_data=False) -> dict:
        """
        Removes torrent with provided id. Local data is deleted if delete_data is True.
        """

        try:
            self.client.remove_torrent(id, delete_data=delete_data)
            return {
                "status": "success",
                "message": f"Removed torrent with id {id} successfully!",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def start(self, id: int) -> dict:
        """
        Starts torrent with provided id.
        """

        try:
            self.client.start_torrent(id)
            return {
                "status": "success",
                "message": f"Started torrent with id {id} successfully",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def pause(self, id: int) -> dict:
        """
        Pauses torrent with provided id.
        """

        try:
            self.client.stop_torrent(id)
            return {
                "status": "success",
                "message": f"Stopped torrent with id {id} successfully",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    torrent_handler = Pirate()
    print(torrent_handler.list())
    # print(torrent_handler.start(1))
    # print(torrent_handler.remove(1, delete_data=True))
