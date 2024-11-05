from pytest import mark

from tests.integration.repositories.fii_csv_repository.fii_csv_repository_fixtures import (
    FiiCSVRepositoryFixtures,
)


class TestGet(FiiCSVRepositoryFixtures):
    @mark.asyncio
    async def test_should_return_fii_when_exists(self, repository):
        fii = await repository.get("BCRI11")
        assert fii.ticker == "bcri11"

    @mark.asyncio
    async def test_should_return_fii_when_exists_and_ticker_is_lower(self, repository):
        fii = await repository.get("bcri11")
        assert fii.ticker == "bcri11"

    @mark.asyncio
    async def test_should_return_none_when_not_exists(self, repository):
        fii = await repository.get("CRI11")
        assert not fii
