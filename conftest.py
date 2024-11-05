import shutil

import pytest

from app_config import CSV_DIR

csv_template_path = CSV_DIR.joinpath("fiis_db_test_template.csv")
csv_test_path = CSV_DIR.joinpath("fiis_db_test.csv")


@pytest.fixture(scope="class", autouse=True)
def reset_fiis_db_csv_test():
    shutil.copy(csv_template_path, csv_test_path)
