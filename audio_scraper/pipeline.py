from argparse import ArgumentParser
from pathlib import Path

from loguru import logger as log
import toml
from pydub import AudioSegment

from audio_scraper.audio_segmenter import AudioSegmenter
from audio_scraper.transcript_filter import TranscriptFilter
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
    transcript_filter: TranscriptFilter

    def __init__(self, config: PipelineConfig):
        Path(config.data_dir).mkdir(exist_ok=True)

        self.scraper = YouTubeChannelScraper(config.data_dir)
        self.segmenter = AudioSegmenter(config.data_dir)
        self.audio_filter = AudioFilter(config.data_dir)
        self.transcriber = Transcriber(config.data_dir, config.transcriber_model_size)
        self.transcript_filter = TranscriptFilter(config.data_dir)

        self.config = config

    def scrape(self) -> list[Path]:
        filepaths = self.scraper(self.config.youtube_channels)
        dur_hours = sum([AudioSegment.from_file(fp).duration_seconds for fp in filepaths]) / 3600
        log.info(f"Scraped a total of {dur_hours:.2f}hrs of audio.")
        return filepaths

    def segment(self, filepaths: list[Path]) -> list[Path]:
        chunk_paths = [cp for cps in list(map(self.segmenter, filepaths)) for cp in cps]
        log.info(f"Split {len(filepaths)} files into {len(chunk_paths)} chunks.")
        return chunk_paths

    def filter_audio(self, filepaths: list[Path]) -> list[Path]:
        filepaths = list(filter(self.audio_filter, filepaths))
        dur_hours = sum([AudioSegment.from_file(cp).duration_seconds for cp in filepaths]) / 3600
        log.info(f"Filtered down to {len(filepaths)} chunks ({dur_hours:.2f}hrs).")
        return filepaths

    def transcribe(self, filepaths: list[Path]) -> list[Path]:
        filepaths = list(map(self.transcriber, filepaths))
        log.info(f"Transcribed {len(filepaths)} chunks.")
        return filepaths

    def filter_text(self, filepaths: list[Path]) -> list[Path]:
        filepaths = list(filter(self.transcript_filter, filepaths))
        log.info(f"Filtered down to {len(filepaths)} transcripts.")
        return filepaths

    def run(self):
        filepaths = self.scrape()
        chunk_paths = self.segment(filepaths)
        chunk_paths = self.filter_audio(chunk_paths)
        transcript_paths = self.transcribe(chunk_paths)
        transcript_paths = self.filter_text(transcript_paths)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config.toml"))
    return parser.parse_args()


def refilter():
    '''
    Only run the audio and text filters on preexisting data.
    '''
    args = parse_args()
    config_dict = toml.loads(args.config.read_text())
    config = PipelineConfig(**config_dict)

    pipeline = Pipeline(config)

    chunk_paths = list(pipeline.segmenter.chunks_dir.rglob("*.wav"))
    log.info(f"Found {len(chunk_paths)} chunks paths")
    chunk_paths = pipeline.filter_audio(chunk_paths)

    transcript_paths = list(pipeline.transcriber.transcript_dir.rglob("*.txt"))
    log.info(f"Found {len(transcript_paths)} transcript paths")
    transcript_paths = pipeline.filter_text(transcript_paths)


def run_all():
    '''
    Run the entire pipeline.
    '''
    args = parse_args()
    config_dict = toml.loads(args.config.read_text())
    config = PipelineConfig(**config_dict)

    pipeline = Pipeline(config)
    pipeline.run()
