import logging
import os
import ssl

# Necessário em redes corporativas com proxy SSL que intercepta HTTPS
os.environ.setdefault("CURL_CA_BUNDLE", "")
os.environ.setdefault("REQUESTS_CA_BUNDLE", "")
ssl._create_default_https_context = ssl._create_unverified_context  # type: ignore[attr-defined]

from config.settings import settings
from core.speech_to_text.base import Segment, SpeechToTextEngine, Transcript

logger = logging.getLogger(__name__)


class WhisperEngine(SpeechToTextEngine):
    def __init__(self) -> None:
        self._model = None

    def is_ready(self) -> bool:
        try:
            return True
        except ImportError:
            return False

    def _load_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            logger.info(
                "Carregando Whisper (%s) em %s ...",
                settings.whisper_model,
                settings.whisper_device,
            )
            self._model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type="int8",
            )
            logger.info("Whisper carregado.")
        return self._model

    def transcribe(self, wav_path: str) -> Transcript:
        model = self._load_model()
        logger.info("Transcrevendo '%s' com Whisper ...", wav_path)

        segments_iter, info = model.transcribe(
            wav_path,
            language=settings.whisper_language,
            vad_filter=True,
        )

        segments = [
            Segment(
                start=s.start,
                end=s.end,
                text=s.text.strip(),
                confidence=s.avg_logprob,
            )
            for s in segments_iter
            if s.text.strip()
        ]

        logger.info(
            "Whisper concluído: %d segmentos, idioma detectado=%s.",
            len(segments),
            info.language,
        )
        return Transcript(segments=segments, language=info.language)
