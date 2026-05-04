import logging

from core.ai_clients.base_client import BaseAIClient
from core.ai_clients.cloud_client import ClaudeClient

logger = logging.getLogger(__name__)


def _build_providers() -> list[BaseAIClient]:
    """Constrói a lista de providers disponíveis em tempo de execução.
    Providers cujos pacotes não estão instalados são ignorados silenciosamente."""
    providers: list[BaseAIClient] = [ClaudeClient()]

    try:
        from core.ai_clients.openai_client import OpenAIClient
        providers.append(OpenAIClient())
    except ImportError:
        logger.debug("openai não instalado — provider OpenAI ignorado.")

    # Gemini desabilitado: google-generativeai conflita com protobuf>=6 (Streamlit)
    return providers


class FallbackClient(BaseAIClient):
    def __init__(self) -> None:
        self._providers = _build_providers()

    def is_available(self) -> bool:
        return any(p.is_available() for p in self._providers)

    def complete(self, system: str, prompt: str) -> str:
        errors: list[str] = []

        for provider in self._providers:
            if not provider.is_available():
                continue
            try:
                return provider.complete(system, prompt)
            except Exception as exc:
                logger.warning(
                    "%s falhou, tentando próximo provider. Erro: %s",
                    type(provider).__name__,
                    exc,
                )
                errors.append(f"{type(provider).__name__}: {exc}")

        raise RuntimeError(
            "Nenhum provider de IA disponível ou todos falharam.\n"
            + "\n".join(errors)
        )
