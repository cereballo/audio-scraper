import os
from pathlib import Path


class TranscriptFilter:

    data_dir: Path

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    @staticmethod
    def _by_num_words(transcript: str, min_words: int, max_words: int) -> bool:
        return min_words < len(transcript.split()) < max_words

    def __call__(self, transcript_path: Path) -> bool:
        transcript = transcript_path.read_text()

        keep_transcript = self._by_num_words(transcript, 3, 50)

        if keep_transcript:
            return True

        os.remove(transcript_path)
        return False
