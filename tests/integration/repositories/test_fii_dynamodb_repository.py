import uuid

import pytest

from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiDynamoDbRepositoryIntegration:

    @pytest.fixture
    def repository(self, dynamodb_test_config):
        from app_config import AppConfig

        config = AppConfig()
        # Use unique table name for isolation
        table_name = f"{config.dynamodb_table_name}_{uuid.uuid4().hex[:8]}"
        return FiiDynamoDBRepository(table_name)

    @pytest.mark.asyncio
    async def test_save_and_get_fii(self, repository, clean_dynamodb_table):
        fii = FiiDomainFactory.build()

        await repository.add(fii)
        result = await repository.get(fii.ticker)

        assert result is not None
        assert result.ticker == fii.ticker
        assert result.p_vp == fii.p_vp
        assert result.segment == fii.segment

    @pytest.mark.asyncio
    async def test_save_overwrites_existing_fii(self, repository, clean_dynamodb_table):
        fii = FiiDomainFactory.build()
        await repository.add(fii)

        fii.p_vp = 1.50
        await repository.add(fii)
        result = await repository.get(fii.ticker)

        assert result.p_vp == 1.50

    @pytest.mark.asyncio
    async def test_get_nonexistent_fii_returns_none(self, repository, clean_dynamodb_table):
        result = await repository.get("NONEXISTENT11")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_empty_table(self, repository, clean_dynamodb_table):
        result = await repository.list()

        assert result == []

    @pytest.mark.asyncio
    async def test_list_multiple_fiis(self, repository, clean_dynamodb_table):
        fii1 = FiiDomainFactory.build(ticker="TEST11")
        fii2 = FiiDomainFactory.build(ticker="DEMO11")

        await repository.add(fii1)
        await repository.add(fii2)
        result = await repository.list()

        assert len(result) == 2
        tickers = [fii.ticker for fii in result]
        assert "TEST11" in tickers
        assert "DEMO11" in tickers

    @pytest.mark.asyncio
    async def test_table_creation_on_first_operation(self, repository):
        fii = FiiDomainFactory.build()
        await repository.add(fii)

        # Se chegou até aqui, a tabela foi criada com sucesso
        result = await repository.get(fii.ticker)
        assert result is not None
        assert result.ticker == fii.ticker
