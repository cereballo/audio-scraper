import os
from pathlib import Path

from pydub import AudioSegment


class AudioFilter:

    data_dir: Path

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    @staticmethod
    def _by_duration(chunk: AudioSegment, min_seconds: float, max_seconds: float) -> bool:
        return min_seconds <= chunk.duration_seconds <= max_seconds

    def __call__(self, filepath: Path) -> bool:
        audio_seg = AudioSegment.from_file(filepath)
        if not self._by_duration(audio_seg, 2, 12):
            os.remove(filepath)
            return False
        return True
