import json
import logging
import uuid
from pathlib import Path

from config.settings import settings
from core.report import Report

logger = logging.getLogger(__name__)


class ReportService:
    def __init__(self) -> None:
        self._reports_dir = Path(settings.data_dir) / "reports"
        self._reports_dir.mkdir(parents=True, exist_ok=True)

    def save(self, report: Report) -> Path:
        filename = f"{report.data[:10]}_{uuid.uuid4().hex[:8]}.json"
        path = self._reports_dir / filename
        path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info("Relatório salvo em '%s'.", path)
        return path

    def load(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def list_all(self) -> list[Path]:
        return sorted(self._reports_dir.glob("*.json"), reverse=True)
