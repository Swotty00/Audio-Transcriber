import logging
import os
import tempfile

from core.audio.processor import to_vosk_wav
from core.speech_to_text.base import Transcript
from services.transcription_service import TranscriptionService

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self) -> None:
        self._transcription = TranscriptionService()

    def run_from_path(self, file_path: str) -> Transcript:
        """Recebe path de qualquer formato suportado e retorna o Transcript."""
        wav_path = to_vosk_wav(file_path)
        try:
            return self._transcription.transcribe(wav_path)
        finally:
            os.unlink(wav_path)

    def run_from_bytes(self, audio_bytes: bytes, suffix: str = ".wav") -> Transcript:
        """Recebe bytes de áudio (ex: upload via API) e retorna o Transcript."""
        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        try:
            tmp.write(audio_bytes)
            tmp.close()
            return self.run_from_path(tmp.name)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
