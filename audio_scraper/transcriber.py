from pathlib import Path
from typing import Literal
import warnings

from loguru import logger as log
from tqdm import tqdm
import whisper

warnings.filterwarnings("ignore")
MODEL = Literal["tiny", "base", "small", "medium", "large"]


class Transcriber:
    """
    Transcribes audio using OpenAI's Whisper model.
    """

    transcript_dir: Path
    model: whisper.Whisper

    def __init__(self, data_dir: Path, model_size: MODEL):
        self.transcript_dir = data_dir / "transcripts"
        self.transcript_dir.mkdir(exist_ok=True, parents=True)

        self.model = whisper.load_model(model_size)

    def __call__(self, filepath: Path, skip_existing: bool = False) -> Path:
        basename = filepath.parent.name
        download_dir = self.transcript_dir / basename
        download_dir.mkdir(exist_ok=True)

        filename = Path(filepath).name.split(".")[0]
        result_path = download_dir / f"{filename}.txt"

        if result_path.exists() and skip_existing:
            log.warning(f"{result_path} exists. Skipping.")
            return result_path

        result = self.model.transcribe(str(filepath))
        transcript = result["text"]
        result_path.write_text(transcript)

        return result_path


def transcribe():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=Path)
    parser.add_argument("--model", choices=MODEL.__args__, default="tiny")
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    transcriber = Transcriber(args.data_dir, args.model)

    audio_files = list((args.data_dir / "chunks").rglob("*"))
    audio_files = list(filter(lambda f: f.is_file(), audio_files))
    for af in tqdm(audio_files):
        transcriber(str(af), args.skip_existing)
