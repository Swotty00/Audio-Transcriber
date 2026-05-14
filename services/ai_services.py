import json
import logging

import asyncio

from concurrent.futures import ThreadPoolExecutor
from core.ai_clients.local_client import LocalClient
from core.report import Origem, Prioridade, Report
from core.speech_to_text.base import Transcript

logger = logging.getLogger(__name__)

_SYSTEM_STRUCTURE = """Você é um assistente de TI. Sua tarefa é converter relatos bagunçados em JSON estruturado.
Retorne APENAS o JSON puro, sem markdown (```).

Regras de Redação:
- Não tente inventar termos técnicos complexos.
- Apenas limpe o texto do usuário: remova gírias, palavrões e repetições.
- Mantenha o idioma original (Português Brasil) e use acentuação correta.
- Se o relato for vago, mantenha-o simples. Ex: "Problema não especificado no botão de envio".

Campos:
- relato: resumo direto e limpo (string)
- prioridade: "baixa" | "média" | "alta" | "crítica"
- origem: "frontend" | "backend" | "infra" | "banco" | "outro"
- url: URL ou null
"""


_ORIGENS_VALIDAS = {"frontend", "backend", "infra", "banco", "outro"}
_PRIORIDADES_VALIDAS = {"baixa", "média", "alta", "crítica"}

_executor = ThreadPoolExecutor(max_workers=3)

class AIService:
    def __init__(self) -> None:
        self._client = LocalClient()

    def is_available(self) -> bool:
        return self._client.is_available()
  
    async def structure_report_async(self, text: str, relator: str) -> Report:
        """Versão async: não bloqueia o event loop do FastAPI."""
        if not self.is_available():
            raise RuntimeError("Nenhuma chave de IA configurada no .env.")
        loop = asyncio.get_event_loop()
        logger.info("Estruturando relato via IA.")
        raw = await loop.run_in_executor(
        _executor,
        lambda: self._client.complete(system=_SYSTEM_STRUCTURE, prompt=f"...\n\n{text}")
    )

        try:
            data = json.loads(str(raw))
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM retornou JSON inválido: {e}\nResposta: {raw}") from e

        return Report(
            relator=relator,
            relato=data.get("relato", text),
            prioridade=data.get("prioridade", "média") if data.get("prioridade", "média") in _PRIORIDADES_VALIDAS else "média",
            origem=data.get("origem", "outro") if data.get("origem", "outro") in _ORIGENS_VALIDAS else "outro",
            status="Bruto",
            url=data.get("url"),
        )
