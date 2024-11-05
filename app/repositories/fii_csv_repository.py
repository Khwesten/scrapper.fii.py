import csv
import os
from datetime import datetime
from typing import Dict, List, Optional

from app.domain.fii_domain import FiiDomain
from app.repositories.fii_repository import FiiRepository
from app_config import CSV_DIR


class FiiCSVRepository(FiiRepository):
    def __init__(self, csv_path: Optional[str] = None) -> None:
        self.csv_path = csv_path or CSV_DIR.joinpath("fiis_db.csv")
        self.fiis = self._load_fiis()

    async def add(self, fii: FiiDomain) -> int:
        fii_persisted = self.fiis.get(fii.ticker.lower())

        if fii_persisted:
            return 0

        self.fiis[fii.ticker.lower()] = fii
        self._save_fiis()
        return 1

    async def get(self, ticker: str) -> Optional[FiiDomain]:
        return self.fiis.get(ticker.lower())

    async def list(self) -> List[FiiDomain]:
        return self.fiis.values()

    def _load_fiis(self) -> Dict[str, FiiDomain]:
        fiis = {}
        if os.path.isfile(self.csv_path):
            with open(self.csv_path, mode="r", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    fiis[row["ticker"].lower()] = self._build_fii(row)
        return fiis

    def _save_fiis(self) -> None:
        with open(self.csv_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(
                [
                    "ticker",
                    "dy_12",
                    "last_dividend",
                    "last_price",
                    "p_vp",
                    "segment",
                    "duration",
                    "last_12_month_evaluation",
                    "current_month_evaluation",
                    "start_date",
                    "dialy_liquidity",
                ]
            )
            for fii in self.fiis.values():
                writer.writerow(
                    [
                        fii.ticker,
                        fii.dy_12,
                        fii.last_dividend,
                        fii.last_price,
                        fii.p_vp,
                        fii.segment,
                        fii.duration,
                        fii.last_12_month_evaluation,
                        fii.current_month_evaluation,
                        fii.start_date.strftime("%Y-%m-%d") if fii.start_date else "",
                        fii.dialy_liquidity,
                    ]
                )

    def _build_fii(self, row: Dict[str, str]) -> FiiDomain:
        return FiiDomain(
            ticker=row["ticker"],
            dy_12=float(row["dy_12"]) if row["dy_12"] else 0.0,
            last_dividend=float(row["last_dividend"]) if row["last_dividend"] else 0.0,
            last_price=float(row["last_price"]) if row["last_price"] else 0.0,
            p_vp=float(row["p_vp"]) if row["p_vp"] else 0.0,
            segment=row["segment"],
            duration=row["duration"],
            last_12_month_evaluation=float(row["last_12_month_evaluation"]) if row["last_12_month_evaluation"] else 0.0,
            current_month_evaluation=float(row["current_month_evaluation"]) if row["current_month_evaluation"] else 0.0,
            start_date=datetime.strptime(row["start_date"], "%Y-%m-%d").date() if row["start_date"] else None,
            dialy_liquidity=float(row["dialy_liquidity"]) if row["dialy_liquidity"] else 0.0,
        )
