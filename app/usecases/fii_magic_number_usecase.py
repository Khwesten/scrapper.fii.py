from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel

from app.domain.fii_domain import FiiDomain
from app.repositories.fii_repository import FiiRepository
from app.repositories.fii_repository_factory import FiiRepositoryFactory


class MagicNumberResponse(BaseModel):
    ticker: str
    magic_number: int
    quotas_for_invested_value: int
    dividend_for_invested_value: Decimal
    invested_value: int
    fii: FiiDomain


class FiiMagicNumberUseCase:
    def __init__(
        self,
        invested_value: Optional[int] = None,
        fii_repository: FiiRepository = None,
    ) -> None:
        self.invested_value = invested_value or 10000
        self.fii_repository = fii_repository or FiiRepositoryFactory.create()

    async def execute(self) -> List[MagicNumberResponse]:
        fiis = await self.fii_repository.list()

        magic_numbers = []
        for fii in fiis:
            magic_numbers.append(self._calculate_magic_number(fii))

        return magic_numbers

    def _calculate_magic_number(self, fii: FiiDomain) -> MagicNumberResponse:
        quotas_for_invested_value = int(self.invested_value / fii.last_price)
        magic_number = int(fii.last_price / fii.last_dividend)
        dividend_for_invested_value = Decimal(quotas_for_invested_value * fii.last_dividend)

        return MagicNumberResponse(
            **{
                "ticker": fii.ticker,
                "magic_number": magic_number,
                "quotas_for_invested_value": quotas_for_invested_value,
                "dividend_for_invested_value": dividend_for_invested_value,
                "invested_value": self.invested_value,
                "fii": fii,
            }
        )
