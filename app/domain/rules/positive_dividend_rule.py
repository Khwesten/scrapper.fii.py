from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class PositiveDividendRule(FiiRule):
    MESSAGE: str = "Dividend must be positive"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        return fii.last_dividend > 0
