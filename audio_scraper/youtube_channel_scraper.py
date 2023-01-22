from pathlib import Path

import yt_dlp


class YouTubeChannelScraper:

    audio_dir: Path

    def __init__(self, data_dir: Path = Path("data")):
        self.audio_dir = data_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

    def _scrape_channel(self, channel_url: str) -> list[str]:
        ydl_opts = {
            "format": "mp4/wav/best",
            "paths": {
                "home": str(self.audio_dir)
            },
            "outtmpl" : '%(channel)s [youtube2-%(channel_id)s]/%(title)s [%(id)s].%(ext)s',
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "m4a",
                }
            ],
            "download-archive": ".ytdlp-archive"
        }

        filepaths = []
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url)
                filepaths = []
                for entry in info["entries"]:
                    requested_downloads = entry.get("requested_downloads")
                    if requested_downloads:
                        filepaths.append(requested_downloads[0]["filepath"])
        except Exception as e: 
            pass
        return filepaths

    def __call__(self, channel_urls: list[str]) -> list[str]:
        filepaths = []
        for url in channel_urls:
            _filepaths = self._scrape_channel(url)
            filepaths.extend(_filepaths)
        return filepaths
