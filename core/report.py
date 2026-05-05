from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


Prioridade = Literal["baixa", "média", "alta", "crítica"]
Status = Literal["Bruto", "Corrigido"]
Origem = Literal["frontend", "backend", "infra", "banco", "outro"]


@dataclass
class Report:
    relator: str
    relato: str
    prioridade: Prioridade
    origem: Origem
    status: Status = "Bruto"
    data: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    url: str | None = None
    resposta_dev: str | None = None

    def to_dict(self) -> dict:
        return {
            "relator": self.relator,
            "status": self.status,
            "prioridade": self.prioridade,
            "data": self.data,
            "origem": self.origem,
            "url": self.url,
            "relato": self.relato,
            "resposta_dev": self.resposta_dev,
        }
