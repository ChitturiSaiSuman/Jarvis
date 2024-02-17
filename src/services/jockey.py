#!/usr/bin/python3

import logging
import mimetypes
import traceback

import hachoir
import mutagen.flac
import mutagen.mp3
import mutagen.wave
import pygame
import tinytag

from src.common.config import Constants

# class PlayList:
#     def __init__(self):


class Jockey:
    """
    Jockey is a Music Player built on pygame.
    Basic functionality includes:
        - Add songs to playlist
        - Play, Pause, Stop songs
        - Play playlist
    Advanced functionality includes:
        - Shuffle playlist
        - Repeat playlist
        - Repeat song
        - Save playlist to a file
    """

    def __init__(self):
        pygame.init()
        self.playlist = []
        self.current_song = None

    def add_to_queue(self, file_path: str) -> dict:
        try:
            self.playlist.append(file_path)
            return {"status": "success", "message": f"Added {file_path} to playlist"}
        except Exception as e:
            return {"status": "error", "message": traceback.format_exc()}

    def play(self):
        if self.current_song is None:
            if self.playlist:
                self.current_song = self.playlist[0]
                pygame.mixer.music.load(self.playlist[0])
                pygame.mixer.music.play()
        else:
            pygame.mixer.music.unpause()

    def pause(self):
        if self.current_song is not None:
            pygame.mixer.music.pause()

    def stop(self):
        if self.current_song is not None:
            pygame.mixer.music.stop()
            self.current_song = None

    def play_playlist(self):
        if self.playlist:
            for song in self.playlist:
                self.current_song = pygame.mixer.music.load(song)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    continue
            self.current_song = None

    def quit(self):
        pygame.mixer.music.stop()
        pygame.quit()


# Example usage
# player = MusicPlayer()
# player.add_to_playlist("/path/to/song1.mp3")
# player.add_to_playlist("/path/to/song2.mp3")
# player.play()
