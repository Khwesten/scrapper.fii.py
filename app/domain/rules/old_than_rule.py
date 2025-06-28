from datetime import date, timedelta

from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class OldThanRule(FiiRule):
    ONE_YEAR = timedelta(days=365)
    MESSAGE = "Start date is less than 1 year"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        if fii.start_date is None:
            return True

        today = date.today()
        return fii.start_date <= today - cls.ONE_YEAR
