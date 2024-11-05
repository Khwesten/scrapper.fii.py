from abc import ABC, abstractmethod

from app.domain.fii_domain import FiiDomain


class FiiRepository(ABC):
    @abstractmethod
    async def add(self) -> int:
        pass

    @abstractmethod
    async def get(self, ticker: str) -> FiiDomain:
        pass
