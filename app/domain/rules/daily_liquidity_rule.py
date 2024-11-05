from decimal import Decimal

from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class DailyLiquidityRule(FiiRule):
    ACCEPTABLE_DAILY_LIQUIDITY = Decimal(750000)
    MESSAGE: str = f"No more than {ACCEPTABLE_DAILY_LIQUIDITY} daily liquidity"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        if fii.dialy_liquidity is None:
            return True

        return fii.dialy_liquidity >= cls.ACCEPTABLE_DAILY_LIQUIDITY
