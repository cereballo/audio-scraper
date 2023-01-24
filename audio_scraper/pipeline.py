from argparse import ArgumentParser
from pathlib import Path

from loguru import logger as log
import toml
from pydub import AudioSegment

from audio_scraper.audio_segmenter import AudioSegmenter
from audio_scraper.youtube_channel_scraper import YouTubeChannelScraper
from audio_scraper.transcriber import Transcriber
from audio_scraper.audio_filter import AudioFilter


class PipelineConfig:
    data_dir: Path
    youtube_channels: list[str]
    transcriber_model_size: str

    def __init__(self, data_dir: Path | str, youtube_channels: list[str], transcriber_model_size: str) -> None:
        self.data_dir = Path(data_dir)
        self.youtube_channels = youtube_channels
        self.transcriber_model_size = transcriber_model_size


class Pipeline:

    segmenter: AudioSegmenter
    scraper: YouTubeChannelScraper
    transcriber: Transcriber
    config: PipelineConfig
    audio_filter: AudioFilter

    def __init__(self, config: PipelineConfig):
        Path(config.data_dir).mkdir(exist_ok=True)

        self.scraper = YouTubeChannelScraper(config.data_dir)
        self.segmenter = AudioSegmenter(config.data_dir)
        self.audio_filter = AudioFilter(config.data_dir)
        self.transcriber = Transcriber(config.data_dir, config.transcriber_model_size)

        self.config = config

    def run(self):
        filepaths = self.scraper(self.config.youtube_channels)
        dur_hours = sum([AudioSegment.from_file(fp).duration_seconds for fp in filepaths]) / 3600
        log.info(f"Scraped a total of {dur_hours:.2f}hrs of audio.")

        chunk_paths = [cp for cps in list(map(self.segmenter, filepaths)) for cp in cps]

        log.info(f"Split {len(filepaths)} into {len(chunk_paths)} chunks.")
        chunk_paths = list(filter(self.audio_filter, chunk_paths))
        dur_hours = sum([AudioSegment.from_file(cp).duration_seconds for cp in chunk_paths]) / 3600
        log.info(f"Filtered down to {len(chunk_paths)} chunks ({dur_hours:.2f}hrs).")
        transcripts = list(map(self.transcriber, chunk_paths))
        log.info(f"Transcribed {len(transcripts)} chunks.")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
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
