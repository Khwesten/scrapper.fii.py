import os

import pytest

from app.usecases.fii_list_usecase import FiiListUseCase
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiListUsecaseIntegration:

    @pytest.fixture(autouse=True)
    def setup_dynamodb_env(self):
        os.environ["DYNAMODB_ENDPOINT"] = "http://localhost:8002"
        os.environ["AWS_ACCESS_KEY_ID"] = "dummy"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "dummy"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["DYNAMODB_TABLE_NAME"] = "fiis_test"

        import importlib

        from app.config import database

        importlib.reload(database)

        yield

    @pytest.fixture
    def real_repository(self):
        import uuid

        from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository

        table_name = f"fiis_test_list_{uuid.uuid4().hex[:8]}"
        return FiiDynamoDBRepository(table_name)

    @pytest.fixture
    def usecase(self, real_repository):
        return FiiListUseCase(real_repository)

    @pytest.fixture
    async def clean_table(self, real_repository):
        yield
        try:
            # Como não há método delete, apenas deixamos limpar naturalmente
            pass
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_execute_returns_all_fiis_from_database(self, usecase, real_repository, clean_table):
        fii1 = FiiDomainFactory.build(ticker="TEST11")
        fii2 = FiiDomainFactory.build(ticker="DEMO11")

        await real_repository.add(fii1)
        await real_repository.add(fii2)

        result = await usecase.execute()

        assert len(result) == 2
        tickers = [fii.ticker for fii in result]
        assert "TEST11" in tickers
        assert "DEMO11" in tickers

    @pytest.mark.asyncio
    async def test_execute_returns_empty_list_when_no_fiis(self, usecase, real_repository, clean_table):
        result = await usecase.execute()

        assert result == []

    @pytest.mark.asyncio
    async def test_execute_returns_fiis_with_all_properties(self, usecase, real_repository, clean_table):
        fii = FiiDomainFactory.build(ticker="TEST11")
        await real_repository.add(fii)

        result = await usecase.execute()

        assert len(result) == 1
        returned_fii = result[0]
        assert returned_fii.ticker == fii.ticker
        assert returned_fii.p_vp == fii.p_vp
        assert returned_fii.segment == fii.segment
        assert returned_fii.duration == fii.duration
        assert returned_fii.last_12_month_evaluation == fii.last_12_month_evaluation
        assert returned_fii.current_month_evaluation == fii.current_month_evaluation
        assert returned_fii.last_price == fii.last_price
        assert returned_fii.last_dividend == fii.last_dividend
        assert returned_fii.dy_12 == fii.dy_12
