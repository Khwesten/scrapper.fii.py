import datetime
from datetime import date
from decimal import Decimal


class DataCrawlerConverter:
    DATE_FORMAT = "%d/%m/%Y"

    @staticmethod
    def to_decimal(number_str: str) -> Decimal:
        number_str = number_str.replace("R$", "").replace("%", "").replace(",", ".")
        return Decimal(number_str)

    @staticmethod
    def to_decimal_or_none(number_str: str) -> date:
        try:
            return DataCrawlerConverter.to_decimal(number_str)
        except Exception:
            return None

    @staticmethod
    def to_date_or_none(date_str: str) -> date:
        try:
            return datetime.strptime(date_str, DataCrawlerConverter.DATE_FORMAT).date()
        except Exception:
            return None
