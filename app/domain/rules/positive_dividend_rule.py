from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class PositiviDividendRule(FiiRule):
    MESSAGE: str = f"Negative dividend"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        return fii.last_dividend < 0
