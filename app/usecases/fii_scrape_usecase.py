import asyncio
from typing import List, Optional

from app.domain.fii_domain import FiiDomain
from app.gateways.status_invest_gateway import FiiGateway, StatusInvestGateway
from app.repositories.fii_csv_repository import FiiCSVRepository
from app.repositories.fii_repository import FiiRepository


class FiiScrapeUseCase:
    def __init__(
        self,
        fii_repository: Optional[FiiRepository] = None,
        fii_gateway: Optional[FiiGateway] = None,
        max_concurrent_requests: Optional[int] = None,
    ) -> None:
        max_concurrent_requests = max_concurrent_requests or 1
        self.fii_repository = fii_repository or FiiCSVRepository()
        self.fii_gateway = fii_gateway or StatusInvestGateway()
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)

    async def execute(self, tickers: List[str] = None) -> List[FiiDomain]:
        fiis = []
        tickers = tickers or await self.fii_gateway.list()

        for ticker in tickers:
            fii = await self._get_or_create_with_semaphore(ticker)
            if fii:
                fiis.append(fii)

        await self.fii_gateway.close()

        return fiis

    async def _get_or_create_with_semaphore(self, ticker: str) -> Optional[FiiDomain]:
        async with self.semaphore:
            if fii := await self.fii_repository.get(ticker):
                return fii

            if fii := await self.fii_gateway.get(ticker):
                return await self.fii_repository.add(fii)

            return None
