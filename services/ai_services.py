import logging

from core.ai_clients.fallback_client import FallbackClient
from core.speech_to_text.base import Transcript

logger = logging.getLogger(__name__)

_SYSTEM_SUMMARIZE = """Você é um assistente especializado em resumir transcrições de áudio.
Escreva resumos concisos, claros e em português, preservando os pontos principais.
Não inclua introduções como "O texto diz que..." — vá direto ao resumo."""

_SYSTEM_CORRECT = """Você é um revisor de textos especializado em transcrições automáticas de áudio.
Corrija erros de reconhecimento de fala, adicione pontuação adequada e melhore a legibilidade.
Mantenha o conteúdo e o sentido originais. Responda apenas com o texto corrigido, sem comentários."""

_SYSTEM_TRANSLATE = """Você é um tradutor profissional. Traduza o texto fornecido de forma fiel e natural.
Responda apenas com o texto traduzido, sem explicações ou comentários adicionais."""


class AIService:
    def __init__(self) -> None:
        self._client = FallbackClient()

    def is_available(self) -> bool:
        return self._client.is_available()

    def summarize(self, transcript: Transcript) -> str:
        if not self.is_available():
            raise RuntimeError("Nenhuma chave de IA configurada no .env.")

        logger.info("Resumindo transcrição (%d segmentos).", len(transcript.segments))
        return self._client.complete(
            system=_SYSTEM_SUMMARIZE,
            prompt=f"Resuma a seguinte transcrição:\n\n{transcript.full_text}",
        )

    def correct(self, transcript: Transcript) -> Transcript:
        """Corrige o texto completo via IA e retorna um novo Transcript com o texto melhorado."""
        if not self.is_available():
            raise RuntimeError("Nenhuma chave de IA configurada no .env.")

        logger.info("Corrigindo transcrição via IA.")
        corrected_text = self._client.complete(
            system=_SYSTEM_CORRECT,
            prompt=f"Corrija a seguinte transcrição:\n\n{transcript.full_text}",
        )

        # Preserva os timestamps originais, atualiza apenas o texto do primeiro segmento
        # (a correção retorna o texto completo sem segmentação)
        from dataclasses import replace
        from core.speech_to_text.base import Segment

        if transcript.segments:
            corrected_segment = Segment(
                start=transcript.segments[0].start,
                end=transcript.segments[-1].end,
                text=corrected_text,
                confidence=1.0,
            )
            return replace(transcript, segments=[corrected_segment])
        return transcript

    def translate(self, transcript: Transcript, target_language: str = "English") -> str:
        if not self.is_available():
            raise RuntimeError("Nenhuma chave de IA configurada no .env.")

        logger.info("Traduzindo transcrição para %s.", target_language)
        return self._client.complete(
            system=_SYSTEM_TRANSLATE,
            prompt=f"Traduza para {target_language}:\n\n{transcript.full_text}",
        )
