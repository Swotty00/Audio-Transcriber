import logging

from config.settings import settings
from core.ai_clients.base_client import BaseAIClient

logger = logging.getLogger(__name__)

MODEL = "gemini-1.5-flash"


class GeminiClient(BaseAIClient):
    def __init__(self) -> None:
        self._model = None

    def is_available(self) -> bool:
        if not settings.gemini_api_key:
            return False
        try:
            import google.generativeai  # noqa: F401
            return True
        except ImportError:
            return False

    def _get_model(self):
        if self._model is None:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            self._model = genai.GenerativeModel(
                model_name=MODEL,
                system_instruction="",  # preenchido em cada chamada
            )
        return self._model

    def complete(self, system: str, prompt: str) -> str:
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)

        logger.info("Chamando Gemini (%s) ...", MODEL)

        model = genai.GenerativeModel(
            model_name=MODEL,
            system_instruction=system,
        )
        response = model.generate_content(prompt)
        text = response.text or ""

        logger.info("Gemini respondeu.")
        return text
