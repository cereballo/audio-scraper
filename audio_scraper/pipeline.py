from argparse import ArgumentParser
from pathlib import Path

import toml
from loguru import logger as log

from audio_scraper.audio_splitter import AudioSplitter
from audio_scraper.youtube_channel_scraper import YouTubeChannelScraper
from audio_scraper.transcriber import Transcriber


class PipelineConfig:
    data_dir: Path
    youtube_channels: list[str]

    def __init__(self, data_dir: Path | str, youtube_channels: list[str]) -> None:
        self.data_dir = Path(data_dir)
        self.youtube_channels = youtube_channels


class Pipeline:

    splitter: AudioSplitter
    scraper: YouTubeChannelScraper
    transcriber: Transcriber
    config: PipelineConfig

    def __init__(self, config: PipelineConfig):
        Path(config.data_dir).mkdir(exist_ok=True)

        self.scraper = YouTubeChannelScraper(config.data_dir)
        self.splitter = AudioSplitter(config.data_dir)
        self.transcriber = Transcriber(config.data_dir)

        self.config = config

    def _process_file(self, filepath: str):
        for cp in self.splitter(filepath):
            self.transcriber(cp)

    def run(self):
        for fp in self.scraper(self.config.youtube_channels):
            self._process_file(fp)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.toml"), help="Path to config file.")
    return parser.parse_args()


def collect():
    args = parse_args()
    config_dict = toml.loads(args.config.read_text())
    config = PipelineConfig(**config_dict)
    pipeline = Pipeline(config)
    pipeline.run()


if __name__ == "__main__":
    collect()
