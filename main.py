import asyncio
import os
from app_config import ROOT_DIR
from app.lib.csv_output_writer import CSVOutputWriter
from app.usecases.fii_analyser_usecase import FiiAnalyserUsecase

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

output_path = f"{ROOT_DIR}/csv/fiis.csv"
output_dir = os.path.dirname(output_path)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

loop = asyncio.get_event_loop()


async def main():
    analyser = FiiAnalyserUsecase(percentage=8)
    fiis = await analyser.execute()
    CSVOutputWriter(output_path).execute(fiis)


if __name__ == "__main__":
    asyncio.run(main())
