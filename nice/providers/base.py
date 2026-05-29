from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Kontrak yang harus diikuti semua LLM provider."""

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        """Kirim messages, terima response sebagai string."""
        pass

    @abstractmethod
    def name(self) -> str:
        """Nama provider ini."""
        pass