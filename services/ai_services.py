import json
import logging

from core.ai_clients.local_client import LocalClient
from core.report import Origem, Prioridade, Report
from core.speech_to_text.base import Transcript

logger = logging.getLogger(__name__)

_SYSTEM_STRUCTURE = """Você é um assistente especializado em estruturar relatos de problemas de TI.
A partir de um texto livre (pode ser transcrição de voz ou texto digitado), extraia as informações
e retorne APENAS um JSON válido, sem markdown, sem explicações, sem texto adicional.

Campos obrigatórios:
- relato: descrição clara e objetiva do problema (string)
- prioridade: "baixa" | "média" | "alta" | "crítica"
- origem: "frontend" | "backend" | "infra" | "banco" | "outro"
- url: URL mencionada ou null

Regras:
- Se não conseguir determinar a prioridade, use "média"
- Se não conseguir determinar a origem, use "outro"
- O relato deve ser uma versão limpa e estruturada do problema, não uma cópia literal
- Responda SOMENTE com o JSON, sem ```json ou qualquer outro texto"""


class AIService:
    def __init__(self) -> None:
        self._client = LocalClient()

    def is_available(self) -> bool:
        return self._client.is_available()
  
    def structure_report(self, text: str, relator: str) -> Report:
        if not self.is_available():
            raise RuntimeError("Nenhuma chave de IA configurada no .env.")

        logger.info("Estruturando relato via IA.")
        raw = self._client.complete(
            system=_SYSTEM_STRUCTURE,
            prompt=f"Estruture o seguinte relato de problema de TI:\n\n{text}",
        )

        try:
            data = json.loads(str(raw))
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM retornou JSON inválido: {e}\nResposta: {raw}") from e

        return Report(
            relator=relator,
            relato=data.get("relato", text),
            prioridade=data.get("prioridade", "média"),
            origem=data.get("origem", "outro"),
            url=data.get("url"),
        )
