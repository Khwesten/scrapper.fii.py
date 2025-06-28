from typing import List

from app.domain.fii_domain import FiiDomain
from app.domain.rules.current_month_evaluation_rule import CurrentMonthEvaluationRule
from app.domain.rules.daily_liquidity_rule import DailyLiquidityRule
from app.domain.rules.fii_rule import FiiRule
from app.domain.rules.indeterminated_duration_rule import IndeterminatedDurationRule
from app.domain.rules.last_12_month_evaluation_rule import Last12MonthEvaluationRule
from app.domain.rules.minimum_dy_rule import MinimumDyRule
from app.domain.rules.old_than_rule import OldThanRule
from app.domain.rules.positive_dividend_rule import PositiveDividendRule
from app.domain.rules.pvp_rule import PVPRule
from app.libs.logger import logger


class FiiValidator:
    def __init__(self, *rules: List[FiiRule]) -> None:
        self.rules = rules

    def validate(self, fii: FiiDomain) -> bool:
        for rule in self.rules:
            if not rule.validate(fii):
                logger.info(f"DIDNT VALIDATED - {fii.ticker.upper()}: {rule.MESSAGE}")
                return False

        return True


class FiiValidatorFactory:
    @staticmethod
    def build() -> FiiValidator:
        return FiiValidator(
            CurrentMonthEvaluationRule,
            Last12MonthEvaluationRule,
            PVPRule,
            OldThanRule,
            IndeterminatedDurationRule,
            DailyLiquidityRule,
            PositiveDividendRule,
            MinimumDyRule,
        )
