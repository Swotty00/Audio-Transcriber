import logging

from core.report import Report
from services.ai_services import AIService
from services.pipeline_service import PipelineService

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self) -> None:
        self._pipeline = PipelineService()
        self._ai = AIService()

    def from_audio(self, file_path: str, relator: str) -> Report:
        """Recebe um arquivo de áudio e retorna um relatório estruturado."""
        logger.info("Iniciando pipeline de áudio para relatório: '%s'", file_path)
        transcript = self._pipeline.run_from_path(file_path)
        return self._ai.structure_report(transcript.full_text, relator)

    def from_text(self, text: str, relator: str) -> Report:
        """Recebe texto livre e retorna um relatório estruturado."""
        logger.info("Iniciando pipeline de texto para relatório.")
        return self._ai.structure_report(text, relator)
