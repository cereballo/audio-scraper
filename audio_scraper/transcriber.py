from pathlib import Path
import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration


class Transcriber:
    """
    Transcribes audio using OpenAI's Whisper model.
    """

    transcript_dir: Path

    def __init__(self, data_dir: Path):
        self.transcript_dir = data_dir / "transcripts"
        self.transcript_dir.mkdir(exist_ok=True, parents=True)

        self.processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
        self.model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")

    def __call__(self, filepath: str, language: str = "en"):
        wav, _ = librosa.load(filepath, sr=16_000)
        input_features = self.processor(wav, return_tensors="pt", sampling_rate=16_000).input_features 
        forced_decoder_ids = self.processor.get_decoder_prompt_ids(language=language, task="translate")
        predicted_ids = self.model.generate(input_features, forced_decoder_ids=forced_decoder_ids)
        transcript = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

        basename = Path(filepath).parent.name
        download_dir = self.transcript_dir / basename
        download_dir.mkdir(exist_ok=True)
        
        filename = Path(filepath).name.split(".")[0]
        result_path = download_dir / f"{filename}.txt"
        result_path.write_text(transcript)
