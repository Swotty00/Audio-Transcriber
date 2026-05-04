import logging

import anthropic

from config.settings import settings
from core.ai_clients.base_client import BaseAIClient

logger = logging.getLogger(__name__)

MODEL = "claude-haiku-4-5"
MAX_TOKENS = 4096


class ClaudeClient(BaseAIClient):
    def __init__(self) -> None:
        self._client: anthropic.Anthropic | None = None

    def is_available(self) -> bool:
        return bool(settings.anthropic_api_key)

    def _get_client(self) -> anthropic.Anthropic:
        if self._client is None:
            if not self.is_available():
                raise RuntimeError("ANTHROPIC_API_KEY não configurada.")
            self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        return self._client

    def complete(self, system: str, prompt: str) -> str:
        client = self._get_client()
        logger.info("Chamando Claude (%s) ...", MODEL)

        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )

        text = next(
            (block.text for block in response.content if block.type == "text"), ""
        )
        logger.info(
            "Claude respondeu. Tokens: entrada=%d (cache_read=%d), saída=%d",
            response.usage.input_tokens,
            getattr(response.usage, "cache_read_input_tokens", 0),
            response.usage.output_tokens,
        )
        return text
