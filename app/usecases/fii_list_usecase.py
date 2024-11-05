from typing import List

from app.domain.fii_domain import FiiDomain
from app.repositories.fii_csv_repository import FiiCSVRepository
from app.repositories.fii_repository import FiiRepository


class FiiListUseCase:
    def __init__(
        self,
        fii_repository: FiiRepository = None,
    ) -> None:
        self.fii_repository = fii_repository or FiiCSVRepository()

    async def execute(self) -> List[FiiDomain]:
        return await self.fii_repository.list()
