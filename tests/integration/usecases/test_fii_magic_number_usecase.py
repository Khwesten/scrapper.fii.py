import os

import pytest

from app.usecases.fii_magic_number_usecase import FiiMagicNumberUseCase
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiMagicNumberUsecaseIntegration:

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

        table_name = f"fiis_test_magic_{uuid.uuid4().hex[:8]}"
        return FiiDynamoDBRepository(table_name)

    @pytest.fixture
    def usecase(self, real_repository):
        return FiiMagicNumberUseCase(fii_repository=real_repository)

    @pytest.fixture
    async def clean_table(self, real_repository):
        yield
        try:
            # Como não há método delete, apenas deixamos limpar naturalmente
            pass
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_execute_calculates_magic_number_from_database(self, usecase, real_repository, clean_table):
        fii1 = FiiDomainFactory.build(ticker="TEST11", p_vp=0.80, dy_12=8.0)

        fii2 = FiiDomainFactory.build(ticker="DEMO11", p_vp=0.90, dy_12=10.0)

        await real_repository.add(fii1)
        await real_repository.add(fii2)

        result = await usecase.execute()

        expected_magic_number1 = int(fii1.last_price / fii1.last_dividend)
        expected_magic_number2 = int(fii2.last_price / fii2.last_dividend)

        assert len(result) == 2

        fii_results = {r.ticker: r for r in result}
        assert fii_results["TEST11"].magic_number == expected_magic_number1
        assert fii_results["DEMO11"].magic_number == expected_magic_number2

    @pytest.mark.asyncio
    async def test_execute_returns_empty_when_no_fiis(self, usecase, real_repository, clean_table):
        result = await usecase.execute()

        assert result == []

    @pytest.mark.asyncio
    async def test_execute_includes_all_fii_properties(self, usecase, real_repository, clean_table):
        fii = FiiDomainFactory.build(ticker="TEST11")
        await real_repository.add(fii)

        result = await usecase.execute()

        assert len(result) == 1
        fii_result = result[0]

        assert fii_result.ticker == fii.ticker
        assert fii_result.fii.p_vp == fii.p_vp
        assert fii_result.fii.dy_12 == fii.dy_12
        assert fii_result.fii.segment == fii.segment
        assert fii_result.fii.duration == fii.duration
        assert fii_result.fii.last_12_month_evaluation == fii.last_12_month_evaluation
        assert fii_result.fii.current_month_evaluation == fii.current_month_evaluation
        assert fii_result.fii.last_price == fii.last_price
        assert fii_result.fii.last_dividend == fii.last_dividend
        assert hasattr(fii_result, "magic_number")

    @pytest.mark.asyncio
    async def test_execute_handles_edge_case_values(self, usecase, real_repository, clean_table):
        fii = FiiDomainFactory.build(ticker="EDGE11", p_vp=0.0, dy_12=0.0, last_price=1.0, last_dividend=1.0)

        await real_repository.add(fii)

        result = await usecase.execute()

        assert len(result) == 1
        assert result[0].magic_number == 1  # int(1.0 / 1.0) = 1
