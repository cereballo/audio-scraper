from pathlib import Path

from loguru import logger as log
import yt_dlp


class YouTubeChannelScraper:

    audio_dir: Path

    def __init__(self, data_dir: Path = Path("data")):
        self.audio_dir = data_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _get_channel_name(channel_url: str) -> str:
        with yt_dlp.YoutubeDL() as ydl:
            log.info(f"Getting channel info for {channel_url}")
            channel_info = ydl.extract_info(channel_url, download=False)
            return channel_info["channel"]

    def _scrape_channel(self, channel_url: str) -> list[str]:
        channel_name = self._get_channel_name(channel_url)
        log.info(f"Scraping YouTube channel: {channel_name}")
        download_dir = self.audio_dir / channel_name
        download_dir.mkdir(exist_ok=True)

        ydl_opts = {
            "format": "mp4/wav/best",
            "paths": {
                "home": str(download_dir)
            },
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        }

        filepaths = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url)
            filepaths = []
            for entry in info["entries"]:
                requested_downloads = entry.get("requested_downloads")
                if requested_downloads:
                    filepaths.append(requested_downloads[0]["filepath"])

        return filepaths

    def __call__(self, channel_urls: list[str]) -> list[str]:
        filepaths = []
        for url in channel_urls:
            _filepaths = self._scrape_channel(url)
            filepaths.extend(_filepaths)
        return filepaths
