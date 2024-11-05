from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class FiiDomain(BaseModel):
    ticker: str
    p_vp: Decimal
    segment: str
    duration: str
    last_12_month_evaluation: Decimal
    current_month_evaluation: Decimal
    last_price: Decimal
    last_dividend: Decimal
    dy_12: Decimal
    start_date: Optional[date] = None
    dialy_liquidity: Optional[Decimal] = Decimal(0)
