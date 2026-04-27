import logging
import tempfile
from pathlib import Path

from pydub import AudioSegment

from config.constants import (
    MAX_FILE_SIZE_BYTES,
    SUPPORTED_FORMATS,
    VOSK_CHANNELS,
    VOSK_SAMPLE_WIDTH,
)
from config.settings import settings

logger = logging.getLogger(__name__)


def validate(file_path: str) -> None:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    if path.suffix.lower() not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Formato '{path.suffix}' não suportado. "
            f"Formatos aceitos: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    size = path.stat().st_size
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(
            f"Arquivo muito grande ({size / 1024 / 1024:.1f} MB). "
            f"Limite: {MAX_FILE_SIZE_BYTES // 1024 // 1024} MB."
        )


def to_vosk_wav(file_path: str) -> str:
    """
    Converte qualquer formato suportado para WAV mono 16-bit no sample rate
    configurado em settings. Retorna o path de um arquivo temporário.
    O chamador é responsável por deletar o arquivo após o uso.
    """
    validate(file_path)

    logger.info("Convertendo '%s' para WAV Vosk ...", file_path)
    audio = AudioSegment.from_file(file_path)

    audio = (
        audio.set_channels(VOSK_CHANNELS)
             .set_frame_rate(settings.sample_rate)
             .set_sample_width(VOSK_SAMPLE_WIDTH)
    )

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    audio.export(tmp.name, format="wav")
    tmp.close()

    logger.info(
        "Convertido: %.1fs de áudio -> '%s'",
        audio.duration_seconds,
        tmp.name,
    )
    return tmp.name


def get_duration(file_path: str) -> float:
    """Retorna a duração em segundos sem converter o arquivo."""
    audio = AudioSegment.from_file(file_path)
    return audio.duration_seconds
