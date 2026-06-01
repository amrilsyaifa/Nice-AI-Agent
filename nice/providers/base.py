from abc import ABC, abstractmethod
from typing import Iterator

class BaseProvider(ABC):

    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        pass

    @abstractmethod
    def chat_sync(self, messages: list[dict]) -> str:
        pass

    @abstractmethod
    def chat_stream(self, messages: list[dict], tools: list = None) -> Iterator[str]:
        """Stream response tokens as they arrive."""
        pass

    @abstractmethod
    def name(self) -> str:
        pass