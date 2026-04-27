import logging

from core.speech_to_text.base import Transcript
from core.speech_to_text.vosk_engine import VoskEngine

logger = logging.getLogger(__name__)


class TranscriptionService:
    def __init__(self) -> None:
        self._engine = VoskEngine()

    def is_ready(self) -> bool:
        return self._engine.is_ready()

    def transcribe(self, wav_path: str) -> Transcript:
        if not self.is_ready():
            raise RuntimeError(
                "Serviço de transcrição não está pronto. "
                "Verifique se o modelo Vosk foi baixado."
            )
        logger.info("Iniciando transcrição de '%s'.", wav_path)
        return self._engine.transcribe(wav_path)
