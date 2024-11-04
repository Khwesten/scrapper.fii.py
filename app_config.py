import os
from pathlib import Path

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = ROOT_DIR.joinpath("csv")
