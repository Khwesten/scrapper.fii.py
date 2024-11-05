from pytest import mark

from app.repositories.fii_csv_repository import FiiCSVRepository
from tests.factories.fii_domain_factory import FiiDomainFactory
from tests.integration.repositories.fii_csv_repository.fii_csv_repository_fixtures import (
    FiiCSVRepositoryFixtures,
)


class TestAdd(FiiCSVRepositoryFixtures):
    @mark.asyncio
    async def test_should_add_fii(self, repository: FiiCSVRepository):
        fii_domain = FiiDomainFactory.build()

        result = await repository.add(fii_domain)

        assert result == 1

    @mark.asyncio
    async def test_should_return_0_when_try_to_add_with_same_ticker(self, repository: FiiCSVRepository):
        fii_domain = FiiDomainFactory.build()

        result1 = await repository.add(fii_domain)
        result2 = await repository.add(fii_domain)

        assert result1 == 1
        assert result2 == 0
