from yt_dlp import YoutubeDL
from typing import Any
from pydantic import AnyHttpUrl
from looptube.core import LTModel


class LTDownloader(LTModel):
    """Base downloader for Looptube"""

    def __init__(self, url: str | AnyHttpUrl, **kwargs: Any):
        super().__init__(**kwargs)
        self.url = AnyHttpUrl(url) if isinstance(url, str) else url
        self.vid_id = self.url.query.split("v=")[1]

    def download_audio(self, codec: str = "mp3") -> str | None:
        """Download the video"""
        return self.download(codec)

    def download_video(self, codec: str = "mp4") -> str | None:
        """Download the video"""
        return self.download(codec)

    def download_frames(self, codec: str = "mp4") -> str | None:
        """Download the video"""
        return self.download(codec)

    def download(self, codec: str = "mp3") -> str | None:
        """Download the video"""
        cached = self.__video_store__ / f"{self.vid_id}.{codec}"
        _abs = cached.absolute()
        if cached.exists():
            self.__logger__.info(f"Video already cached: {str(_abs)}")
            return str(_abs)

        try:
            self.__logger__.info(f"Downloading video to {self.vid_id}.{codec}")

            ydl_opts = {
                "format": f"{codec}/bestaudio/best",
                "outtmpl": str(self.__video_store__ / f"{self.vid_id}.{codec}"),
                # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
                "postprocessors": [
                    {  # Extract audio using ffmpeg
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": codec,
                    }
                ],
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([str(self.url)])
        except Exception as e:
            self.__logger__.error(f"Error downloading {self.vid_id}: {e}")
            print(e)
            return str(_abs)
        return None
