from decimal import Decimal
from typing import List
from app.domain.fii_domain import FiiDomain
from app.domain.fii_validator import FiiValidatorFactory
from app.gateways.status_invest_gateway import FiiGateway, StatusInvestGateway


class FiiAnalyserUsecase:
    def __init__(
        self,
        percentage: Decimal = None,
        fii_gateway: FiiGateway = None,
        fii_validator_factory: FiiValidatorFactory = None,
        without_analyse: bool = None,
    ) -> None:
        self.percentage = percentage or Decimal(6)
        self.fii_gateway = fii_gateway or StatusInvestGateway()
        self.fii_validator_factory = fii_validator_factory or FiiValidatorFactory
        self.without_analyse = without_analyse or False

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
        fii = await self.fii_gateway.get(ticker)

        if not fii:
            return None

        # TODO: ADD RULES TO CHECK
        # quota holders
        # quota number
        # vacancy rate
        # cap rate
        # monoativo vs multiativo

        if self.without_analyse:
            return fii

        is_valid = self.fii_validator_factory.build().validate(fii)

        if is_valid and fii.dy_12 >= self.percentage and fii.last_dividend > 0 and fii.last_price > 0:
            return fii
