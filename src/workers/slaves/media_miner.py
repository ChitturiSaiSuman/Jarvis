#!/usr/bin/python3

import mimetypes, logging, json, os
import mutagen.flac, mutagen.mp3, mutagen.wave
from concurrent.futures import ThreadPoolExecutor


class Media:
    def __init__(self, file_path: str):
        attributes = [
            "title",
            "duration",
            "album",
            "media_type",
            "file_path",
            "extension",
        ]
        self.__dict__.update((attribute, None) for attribute in attributes)
        self.file_path = file_path
        self.__parse()

    def __parse(self):
        mime_type, encoding = mimetypes.guess_type(self.file_path)
        self.media_type, self.extension = mime_type.split("/")

        if self.media_type == None:
            logging.warning(f"Unable to identify media type for {self.file_path}")
            return

        parsers = {
            "audio": self.__parse_audio,
            "video": self.__parse_video,
        }

        if self.media_type in parsers:
            try:
                parsers[self.media_type]()
            except Exception as e:
                logging.warning(f"Unable to parse {self.file_path}: {e}")
        else:
            logging.warning(f"Unsupported media type: {self.media_type}")

    def __parse_audio(self):
        audio_parsers = {
            "flac": {
                "file": mutagen.flac.FLAC,
                "attributes": {
                    "title": lambda file: file.get("title", None)[0],
                    "duration": lambda file: file.info.length,
                    "album": lambda file: file.get("album", None)[0],
                },
            },
            "mpeg": {
                "file": mutagen.mp3.MP3,
                "attributes": {
                    "title": lambda file: file.get("TIT2", None)[0],
                    "duration": lambda file: file.info.length,
                    "album": lambda file: file.get("TALB", None)[0],
                },
            },
            "x-wav": {
                "file": mutagen.wave.WAVE,
                "attributes": {
                    "title": lambda file: file.get("TIT2", None)[0],
                    "duration": lambda file: file.info.length,
                    "album": lambda file: file.get("TALB", None)[0],
                },
            },
        }

        audio_parser = audio_parsers[self.extension]
        audio_file = audio_parser["file"](self.file_path)
        for attribute, function in audio_parser["attributes"].items():
            self.__dict__[attribute] = function(audio_file)

    def __parse_video(self):
        pass

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return str(self)

    def __lt__(self, other):
        if self.album == None and other.album == None:
            return self.file_path < other.file_path
        elif self.album == None or other.album == None:
            return other.album == None
        elif self.album.lower() != other.album.lower():
            return self.album.lower() < other.album.lower()
        else:
            if self.title == None and other.title == None:
                return self.file_path < other.file_path
            elif self.title == None or other.title == None:
                return other.title == None
            else:
                return self.title.lower() < other.title.lower()

    def __le__(self, other):
        return self < other or self == other

    def __eq__(self, other):
        return self.file_path == other.file_path

    def __ne__(self, other):
        return self.file_path != other.file_path

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return not self < other


class MediaMiner:
    """
    MediaMiner is a class for navigating through a directory, identifying media files,
    and curating a database of local media.

    Attributes:
    - media_directory (str): The base directory to start the media mining process.

    Methods:
    - mine_media(): Traverses the specified directory, identifies media files, and populates the media database.
    """

    def __init__(self, media_directory: str):
        self.media_directory = media_directory
        self.media_database = []

    def mine_media(self):
        with ThreadPoolExecutor() as executor:
            media_files = self._traverse_directory(self.media_directory)

            results = list(executor.map(self._process_media_file, media_files))

            parsed_media = [media for media in results if media is not None]

            self.media_database.extend(parsed_media)

    def _traverse_directory(self, directory):
        media_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                if self._is_media_file(file):
                    media_files.append(os.path.join(root, file))
        return media_files

    def _is_media_file(self, file):
        valid_extensions = {".mp3", ".flac", ".wav"}
        _, extension = os.path.splitext(file)
        return extension.lower() in valid_extensions

    def _process_media_file(self, file_path):
        try:
            media = Media(file_path)
            return media
        except Exception as e:
            logging.warning(f"Error processing {file_path}: {e}")
            return None


if __name__ == "__main__":
    # miner = MediaMiner("/home/suman/Music/")
    # miner.mine_media()
    # print(json.dumps(sorted(miner.media_database), default=lambda x: x.__dict__, indent=4))
    pass