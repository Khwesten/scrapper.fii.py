from pytest import mark

from app.repositories.fii_csv_repository import FiiCSVRepository
from tests.integration.repositories.fii_csv_repository.fii_csv_repository_fixtures import (
    FiiCSVRepositoryFixtures,
)


class TestList(FiiCSVRepositoryFixtures):
    @mark.asyncio
    async def test_should_return_1_fii(self, repository: FiiCSVRepository):
        fiis = await repository.list()
        assert len(fiis) == 1
