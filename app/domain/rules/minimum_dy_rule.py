from decimal import Decimal

from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class MinimumDyRule(FiiRule):
    MINIMUM_DY = Decimal("6.0")
    MESSAGE = f"DY 12 months must be at least {MINIMUM_DY}%"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        if fii.dy_12 is None:
            return False
        
        return fii.dy_12 >= cls.MINIMUM_DY
