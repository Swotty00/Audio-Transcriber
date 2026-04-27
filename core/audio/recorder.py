import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioRecorder:
    """
    Persiste bytes de áudio gravados (vindos da UI) em um arquivo temporário.
    Mantém referência ao último arquivo gravado para limpeza posterior.
    """

    def __init__(self) -> None:
        self._last_path: str | None = None

    def save(self, audio_bytes: bytes, suffix: str = ".wav") -> str:
        """
        Salva bytes de áudio em um temp file. Retorna o path do arquivo.
        Descarta automaticamente o arquivo anterior se houver.
        """
        self._cleanup()

        if not audio_bytes:
            raise ValueError("Nenhum dado de áudio para salvar.")

        tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp.write(audio_bytes)
        tmp.close()

        self._last_path = tmp.name
        logger.info("Áudio gravado salvo em '%s' (%d bytes).", tmp.name, len(audio_bytes))
        return tmp.name

    def _cleanup(self) -> None:
        if self._last_path:
            path = Path(self._last_path)
            if path.exists():
                path.unlink()
                logger.debug("Temp file removido: '%s'.", self._last_path)
            self._last_path = None

    def __del__(self) -> None:
        self._cleanup()
