from decimal import Decimal
from typing import List

from app.domain.fii_domain import FiiDomain
from app.domain.fii_validator import FiiValidatorFactory
from app.repositories.fii_repository import FiiRepository
from app.repositories.fii_repository_factory import FiiRepositoryFactory


class FiiAnalyserUsecase:
    def __init__(
        self,
        percentage: Decimal = None,
        fii_validator_factory: FiiValidatorFactory = None,
        fii_repository: FiiRepository = None,
    ) -> None:
        self.percentage = percentage or Decimal(6)
        self.fii_validator_factory = fii_validator_factory or FiiValidatorFactory
        self.fii_repository = fii_repository or FiiRepositoryFactory.create()

    async def execute(self, tickers: List[str] = None) -> List[FiiDomain]:
        fiis = []
        tickers = tickers or await self.fii_gateway.list()

        for ticker in tickers:
            fii = await self._get(ticker=ticker)
            if fii is not None:
                fiis.append(fii)

        await self.fii_gateway.close()

        return fiis

    async def _get(self, ticker: str) -> FiiDomain:
        fii = await self.fii_repository.get(ticker)

        is_valid = self.fii_validator_factory.build().validate(fii)

        if is_valid and fii.dy_12 >= self.percentage and fii.last_dividend > 0 and fii.last_price > 0:
            return fii
