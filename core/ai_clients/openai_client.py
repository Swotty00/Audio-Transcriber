import logging

from config.settings import settings
from core.ai_clients.base_client import BaseAIClient

logger = logging.getLogger(__name__)

MODEL = "gpt-4o-mini"
MAX_TOKENS = 4096


class OpenAIClient(BaseAIClient):
    def __init__(self) -> None:
        self._client = None

    def is_available(self) -> bool:
        if not settings.openai_api_key:
            return False
        try:
            import openai  # noqa: F401
            return True
        except ImportError:
            return False

    def _get_client(self):
        if self._client is None:
            import openai
            self._client = openai.OpenAI(api_key=settings.openai_api_key)
        return self._client

    def complete(self, system: str, prompt: str) -> str:
        client = self._get_client()
        logger.info("Chamando OpenAI (%s) ...", MODEL)

        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )

        text = response.choices[0].message.content or ""
        logger.info(
            "OpenAI respondeu. Tokens: entrada=%d, saída=%d",
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
        )
        return text
