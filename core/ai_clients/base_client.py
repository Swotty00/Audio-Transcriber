from abc import ABC, abstractmethod


class BaseAIClient(ABC):
    @abstractmethod
    def complete(self, system: str, prompt: str) -> str:
        """Envia um prompt e retorna a resposta como string."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Retorna True se o cliente estiver configurado e disponível."""
        ...
