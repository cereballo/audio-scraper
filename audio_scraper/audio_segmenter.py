import os
from pathlib import Path

from pydub import AudioSegment
from pydub.silence import split_on_silence


class AudioSegmenter:

    chunks_dir: Path

    def __init__(self, data_dir: Path):
        self.chunks_dir = data_dir / "chunks"
        self.chunks_dir.mkdir(parents=True, exist_ok=True)

    def __call__(self, filepath: Path):
        audio_segment = AudioSegment.from_file(str(filepath))
        chunks = split_on_silence(
            audio_segment,
            silence_thresh=-40,
            keep_silence=50,
            seek_step=100,
            min_silence_len=400
        )

        basename = os.path.splitext(Path(filepath).name)[0]
        download_dir = self.chunks_dir / basename
        download_dir.mkdir(exist_ok=True)

        filenames = []
        for idx, chunk in enumerate(chunks):
            filename = str(download_dir / f"{idx}.wav")
            chunk.export(filename, format="wav")
            filenames.append(filename)

        return filenames
