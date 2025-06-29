from decimal import Decimal
from typing import List, Optional

from app.domain.fii_domain import FiiDomain
from app.libs.logger import logger
from app.repositories.fii_repository import FiiRepository


class FiiMemoryRepository(FiiRepository):
    def __init__(self):
        self._fiis = self._get_sample_data()
        logger.info(f"FiiMemoryRepository initialized with {len(self._fiis)} sample FIIs")

    async def add(self, fii: FiiDomain) -> int:
        await self.save(fii)
        return 1

    async def get(self, ticker: str) -> Optional[FiiDomain]:
        return await self.get_by_ticker(ticker)

    async def list(self) -> List[FiiDomain]:
        return self._fiis.copy()

    async def save(self, fii: FiiDomain) -> None:
        existing = next((f for f in self._fiis if f.ticker == fii.ticker), None)
        if existing:
            index = self._fiis.index(existing)
            self._fiis[index] = fii
        else:
            self._fiis.append(fii)

    async def get_by_ticker(self, ticker: str) -> Optional[FiiDomain]:
        return next((f for f in self._fiis if f.ticker == ticker), None)

    async def save_all(self, fiis: List[FiiDomain]) -> None:
        for fii in fiis:
            await self.save(fii)

    def _get_sample_data(self) -> List[FiiDomain]:
        return [
            FiiDomain(
                ticker="BCRI11",
                p_vp=Decimal("0.85"),
                segment="Lajes Corporativas",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("8.5"),
                current_month_evaluation=Decimal("1.2"),
                last_price=Decimal("95.50"),
                dy_12=Decimal("10.5"),
                dialy_liquidity=Decimal("2500000"),
                last_dividend=Decimal("0.89"),
            ),
            FiiDomain(
                ticker="HGRE11",
                p_vp=Decimal("0.92"),
                segment="Híbrido",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("12.8"),
                current_month_evaluation=Decimal("2.1"),
                last_price=Decimal("125.80"),
                dy_12=Decimal("9.8"),
                dialy_liquidity=Decimal("5800000"),
                last_dividend=Decimal("1.03"),
            ),
            FiiDomain(
                ticker="XPLG11",
                p_vp=Decimal("0.78"),
                segment="Logística",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("15.2"),
                current_month_evaluation=Decimal("0.8"),
                last_price=Decimal("98.20"),
                dy_12=Decimal("11.2"),
                dialy_liquidity=Decimal("1200000"),
                last_dividend=Decimal("0.92"),
            ),
            FiiDomain(
                ticker="VILG11",
                p_vp=Decimal("0.88"),
                segment="Shoppings",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("5.4"),
                current_month_evaluation=Decimal("-0.5"),
                last_price=Decimal("88.90"),
                dy_12=Decimal("8.9"),
                dialy_liquidity=Decimal("980000"),
                last_dividend=Decimal("0.66"),
            ),
            FiiDomain(
                ticker="BTLG11",
                p_vp=Decimal("0.95"),
                segment="Logística",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("7.2"),
                current_month_evaluation=Decimal("1.8"),
                last_price=Decimal("105.30"),
                dy_12=Decimal("9.5"),
                dialy_liquidity=Decimal("3200000"),
                last_dividend=Decimal("0.84"),
            ),
            FiiDomain(
                ticker="MXRF11",
                p_vp=Decimal("0.89"),
                segment="Híbrido",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("9.8"),
                current_month_evaluation=Decimal("0.3"),
                last_price=Decimal("10.25"),
                dy_12=Decimal("10.8"),
                dialy_liquidity=Decimal("4500000"),
                last_dividend=Decimal("0.09"),
            ),
            FiiDomain(
                ticker="KNRI11",
                p_vp=Decimal("0.91"),
                segment="Lajes Corporativas",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("6.7"),
                current_month_evaluation=Decimal("1.1"),
                last_price=Decimal("82.40"),
                dy_12=Decimal("9.2"),
                dialy_liquidity=Decimal("1800000"),
                last_dividend=Decimal("0.63"),
            ),
            FiiDomain(
                ticker="HGLG11",
                p_vp=Decimal("0.86"),
                segment="Logística",
                duration="Indeterminado",
                last_12_month_evaluation=Decimal("11.5"),
                current_month_evaluation=Decimal("2.3"),
                last_price=Decimal("162.50"),
                dy_12=Decimal("8.7"),
                dialy_liquidity=Decimal("2100000"),
                last_dividend=Decimal("1.18"),
            ),
        ]
