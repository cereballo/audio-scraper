from argparse import ArgumentParser
from pathlib import Path

from loguru import logger as log
import toml

from audio_scraper.audio_splitter import AudioSplitter
from audio_scraper.youtube_channel_scraper import YouTubeChannelScraper
from audio_scraper.transcriber import Transcriber
from audio_scraper.audio_filter import AudioFilter


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
    audio_filter: AudioFilter

    def __init__(self, config: PipelineConfig):
        Path(config.data_dir).mkdir(exist_ok=True)

        self.scraper = YouTubeChannelScraper(config.data_dir)
        self.splitter = AudioSplitter(config.data_dir)
        self.audio_filter = AudioFilter(config.data_dir)
        self.transcriber = Transcriber(config.data_dir)

        self.config = config

    def run(self):
        filepaths = self.scraper(self.config.youtube_channels)
        chunk_paths = [cp for cps in list(map(self.splitter, filepaths)) for cp in cps]

        log.info(f"Split {len(filepaths)} into {len(chunk_paths)} chunks.")
        chunk_paths = list(filter(self.audio_filter, chunk_paths))
        log.info(f"Filtered down to {len(chunk_paths)} chunks.")
        transcripts = list(map(self.transcriber, chunk_paths))
        log.info(f"Transcribed {len(transcripts)} chunks.")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.toml"), help="Path to config file.")
    return parser.parse_args()


def collect(config: PipelineConfig):
    pipeline = Pipeline(config)
    pipeline.run()


def main():
    args = parse_args()
    config_dict = toml.loads(args.config.read_text())
    config = PipelineConfig(**config_dict)
    collect(config)


if __name__ == "__main__":
    main()
