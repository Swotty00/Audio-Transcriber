import logging

from core.speech_to_text.base import SpeechToTextEngine, Transcript
from core.speech_to_text.whisper_engine import WhisperEngine
from core.speech_to_text.vosk_engine import VoskEngine

logger = logging.getLogger(__name__)


def _build_engine() -> SpeechToTextEngine:
    whisper = WhisperEngine()
    if whisper.is_ready():
        logger.info("Usando WhisperEngine.")
        return whisper
    logger.warning("faster-whisper não instalado — usando VoskEngine.")
    return VoskEngine()


class TranscriptionService:
    def __init__(self) -> None:
        self._engine = _build_engine()

    def is_ready(self) -> bool:
        return self._engine.is_ready()

    def transcribe(self, wav_path: str) -> Transcript:
        logger.info("Iniciando transcrição de '%s'.", wav_path)
        return self._engine.transcribe(wav_path)
