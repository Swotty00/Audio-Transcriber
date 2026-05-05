import logging

from core.ai_clients.base_client import BaseAIClient

logger = logging.getLogger(__name__)

MODEL = "llama3.2"


class LocalClient(BaseAIClient):
    def __init__(self) -> None:
        self._client = None

    def is_available(self) -> bool:
        try:
            import ollama
            ollama.list()
            return True
        except Exception:
            return False

    def _get_client(self):
        if self._client is None:
            import ollama
            self._client = ollama.Client()
        return self._client

    def complete(self, system: str, prompt: str) -> str:
        client = self._get_client()
        logger.info("Chamando Ollama local (%s) ...", MODEL)

        response = client.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )

        text = response.message.content or ""
        logger.info("Ollama respondeu.")
        return text
