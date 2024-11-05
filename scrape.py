import asyncio

from app.usecases.fii_scrape_usecase import FiiScrapeUseCase
from app_config import CSV_DIR

tickers = [
    "BCRI11",
    "BPFF11",
    "CPTS11",
    "HFOF11",
    "KISU11",
    "MFII11",
    "MXRF11",
    "RBFF11",
    "RECR11",
    "VISC11",
    "VINO11",
    "VILG11",
    "HGRU11",
]

output_path = CSV_DIR.joinpath("fiis_db.csv")
loop = asyncio.get_event_loop()


async def main():
    usecase = FiiScrapeUseCase()
    await usecase.execute()


if __name__ == "__main__":
    asyncio.run(main())
