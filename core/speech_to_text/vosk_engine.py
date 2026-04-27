import json
import logging
import wave
from pathlib import Path

from vosk import KaldiRecognizer, Model

from config.constants import VOSK_CHUNK_SIZE
from config.settings import settings
from core.speech_to_text.base import Segment, SpeechToTextEngine, Transcript

logger = logging.getLogger(__name__)


class VoskEngine(SpeechToTextEngine):
    def __init__(self) -> None:
        self._model: Model | None = None

    def is_ready(self) -> bool:
        model_path = Path(settings.vosk_model_path)
        return model_path.exists() and any(model_path.iterdir())

    def _load_model(self) -> Model:
        if self._model is None:
            if not self.is_ready():
                raise RuntimeError(
                    f"Modelo Vosk não encontrado em '{settings.vosk_model_path}'. "
                    "Execute: python scripts/download_models.py"
                )
            logger.info("Carregando modelo Vosk de '%s' ...", settings.vosk_model_path)
            self._model = Model(settings.vosk_model_path)
            logger.info("Modelo carregado.")
        return self._model

    def transcribe(self, wav_path: str) -> Transcript:
        model = self._load_model()
        transcript = Transcript()

        with wave.open(wav_path) as wf:
            if wf.getsampwidth() != 2 or wf.getnchannels() != 1:
                raise ValueError(
                    "O arquivo deve ser WAV mono 16-bit. "
                    "Use core.audio.processor.to_vosk_wav() antes de transcrever."
                )

            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            logger.info("Transcrevendo '%s' ...", wav_path)

            while chunk := wf.readframes(VOSK_CHUNK_SIZE):
                if rec.AcceptWaveform(chunk):
                    self._parse_result(rec.Result(), transcript)

            self._parse_result(rec.FinalResult(), transcript)

        logger.info(
            "Concluído: %d segmentos, %.1fs.",
            len(transcript.segments),
            transcript.duration,
        )
        return transcript

    def _parse_result(self, raw: str, transcript: Transcript) -> None:
        words = json.loads(raw).get("result", [])
        if not words:
            return

        segment_words: list[dict] = []
        for word in words:
            if segment_words:
                gap = word["start"] - segment_words[-1]["end"]
                if gap > 0.7:
                    transcript.segments.append(self._words_to_segment(segment_words))
                    segment_words = []
            segment_words.append(word)

        if segment_words:
            transcript.segments.append(self._words_to_segment(segment_words))

    @staticmethod
    def _words_to_segment(words: list[dict]) -> Segment:
        confidence = sum(w.get("conf", 1.0) for w in words) / len(words)
        return Segment(
            start=words[0]["start"],
            end=words[-1]["end"],
            text=" ".join(w["word"] for w in words),
            confidence=round(confidence, 3),
        )
