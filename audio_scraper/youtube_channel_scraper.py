from pathlib import Path

from loguru import logger as log
from tqdm import tqdm
import yt_dlp


class YouTubeChannelScraper:

    videos_dir: Path

    def __init__(self, data_dir: Path):
        self.videos_dir = data_dir / "videos"
        self.videos_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_channel_name(channel_url: str) -> str:
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            log.info(f"Getting channel info for {channel_url}")
            channel_info = ydl.extract_info(channel_url, download=False)
            return channel_info["channel"]

    def __call__(self, channel_urls: list[str]) -> list[str]:
        for channel_url in channel_urls:
            channel_name = self._get_channel_name(channel_url)
            download_dir = self.videos_dir / channel_name
            download_dir.mkdir(exist_ok=True)

            ydl_opts = {
                "quiet": True,
                "format": "mp4/wav/best",
                "paths": {
                    "home": str(download_dir)
                }
            }

            filepaths = []
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url)
                filepaths = []
                for entry in tqdm(info["entries"], desc=channel_name):
                    requested_downloads = entry.get("requested_downloads")
                    if requested_downloads is None:
                        continue
                    filepaths.append(requested_downloads[0]["filepath"])

        return filepaths
