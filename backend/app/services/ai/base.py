"""Provider interface — all vendors implement this."""
from abc import ABC, abstractmethod
from app.schemas.scope import ScopeModel


class AIProvider(ABC):
    name: str = "base"

    @abstractmethod
    def analyze(self, session_id: str, normalized_md: str, chunks: list) -> ScopeModel:
        raise NotImplementedError
