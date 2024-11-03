from decimal import Decimal
from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class CurrentMonthEvaluationRule(FiiRule):
    ACCEPTABLE_DEVALUATION = -15
    MESSAGE = f"Current month evaluation is less than {ACCEPTABLE_DEVALUATION}%"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        return fii.current_month_evaluation >= Decimal(cls.ACCEPTABLE_DEVALUATION)
