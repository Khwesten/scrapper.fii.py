from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.fii_domain import FiiDomain


class FiiRepository(ABC):
    @abstractmethod
    async def add(self, fii: FiiDomain) -> int:
        pass

    @abstractmethod
    async def get(self, ticker: str) -> Optional[FiiDomain]:
        pass

    @abstractmethod
    async def list(self) -> List[FiiDomain]:
        pass
