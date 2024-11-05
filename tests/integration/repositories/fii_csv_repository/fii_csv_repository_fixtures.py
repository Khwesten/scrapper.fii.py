from pytest import fixture

from app.repositories.fii_csv_repository import FiiCSVRepository
from app_config import CSV_DIR


class FiiCSVRepositoryFixtures:
    @fixture
    def repository(self):
        test_path = CSV_DIR.joinpath("fiis_db_test.csv")
        return FiiCSVRepository(csv_path=test_path)
