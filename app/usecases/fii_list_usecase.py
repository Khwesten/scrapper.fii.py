from typing import List

from app.domain.fii_domain import FiiDomain
from app.repositories.fii_repository import FiiRepository
from app.repositories.fii_repository_factory import FiiRepositoryFactory


class FiiListUseCase:
    def __init__(
        self,
        fii_repository: FiiRepository = None,
    ) -> None:
        self.fii_repository = fii_repository or FiiRepositoryFactory.create()

    async def execute(self) -> List[FiiDomain]:
        return await self.fii_repository.list()
