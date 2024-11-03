from datetime import date
from decimal import Decimal
from typing import Optional
from attr import dataclass


@dataclass
class FiiDomain:
    ticker: str
    p_vp: Decimal
    segment: str
    duration: str
    last_12_month_evaluation: Decimal
    current_month_evaluation: Decimal
    last_price: Decimal
    last_dividend: Decimal
    dy_12: Decimal
    start_date: Optional[date]
    dialy_liquidity: Optional[Decimal]
