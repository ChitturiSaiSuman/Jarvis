import time
import pychromecast
from pychromecast.controllers.youtube import YouTubeController

# Function to discover and connect to Chromecast device
def connect_to_chromecast(device_name):
    chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[device_name])

    if not chromecasts:
        print(f"Chromecast device '{device_name}' not found.")
        return None

    chromecast = chromecasts[0]
    chromecast.wait()
    return chromecast

# Function to cast a YouTube video to Chromecast
def cast_youtube_video(chromecast, video_id):
    youtube = YouTubeController()
    chromecast.register_handler(youtube)
    youtube.play_video(video_id)

# Function to cast a local media file to Chromecast
def cast_local_media(chromecast, media_path):
    mc = chromecast.media_controller
    mc.play_media(media_path, "video/mp4")

if __name__ == "__main__":
    # Replace with the name of your Chromecast device
    chromecast_name = "Tata Play"

    # Replace with the YouTube video ID or local media file path
    youtube_video_id = "XRCIzZHpFtY"
    local_media_path = "/home/suman/Videos/example.mp4"

    # Connect to Chromecast
    chromecast = connect_to_chromecast(chromecast_name)

    if chromecast:
        # Uncomment one of the following lines based on what you want to cast
        # cast_youtube_video(chromecast, youtube_video_id)
        cast_local_media(chromecast, local_media_path)

        # Wait for a while to allow casting to happen
        time.sleep(100)
