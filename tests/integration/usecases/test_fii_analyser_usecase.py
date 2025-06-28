import os

import pytest

from app.usecases.fii_analyser_usecase import FiiAnalyserUsecase
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiAnalyserUsecaseIntegration:

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

        table_name = f"fiis_test_analyser_{uuid.uuid4().hex[:8]}"
        return FiiDynamoDBRepository(table_name)

    @pytest.fixture
    def usecase(self, real_repository):
        return FiiAnalyserUsecase(fii_repository=real_repository)

    @pytest.fixture
    async def clean_table(self, real_repository):
        yield
        try:
            # Como não há método delete, apenas deixamos limpar naturalmente
            pass
        except Exception:
            pass

    @pytest.mark.asyncio
    async def test_execute_filters_fiis_by_all_rules(self, usecase, real_repository, clean_table):
        good_fii = FiiDomainFactory.build(
            ticker="GOOD11",
            p_vp=0.95,  # Valid for PVPRule (0.9 <= p_vp <= 1.1)
            dy_12=8.0,
            last_12_month_evaluation=10.0,
            current_month_evaluation=2.0,
            last_dividend=0.5,
            dialy_liquidity=800000,  # Above minimum 750000
            duration="indeterminado",  # Valid duration (lowercase)
        )

        bad_fii = FiiDomainFactory.build(
            ticker="BAD11",
            p_vp=1.20,
            dy_12=4.0,
            last_12_month_evaluation=-5.0,
            current_month_evaluation=-1.0,
            last_dividend=0.0,
        )

        await real_repository.add(good_fii)
        await real_repository.add(bad_fii)

        result = await usecase.execute()

        assert len(result) == 1
        assert result[0].ticker == "GOOD11"

    @pytest.mark.asyncio
    async def test_execute_returns_empty_when_no_fiis_pass_rules(self, usecase, real_repository, clean_table):
        bad_fii = FiiDomainFactory.build(
            ticker="BAD11",
            p_vp=1.50,
            dy_12=3.0,
            last_12_month_evaluation=-10.0,
            current_month_evaluation=-2.0,
            last_dividend=0.0,
        )

        await real_repository.add(bad_fii)

        result = await usecase.execute()

        assert result == []

    @pytest.mark.asyncio
    async def test_execute_returns_multiple_valid_fiis(self, usecase, real_repository, clean_table):
        good_fii1 = FiiDomainFactory.build(
            ticker="GOOD11",
            p_vp=0.95,  # Valid for PVPRule
            dy_12=9.0,
            last_12_month_evaluation=15.0,
            current_month_evaluation=2.5,
            last_dividend=0.8,
            dialy_liquidity=800000,  # Above minimum 750000
            duration="indeterminado",  # Valid duration (lowercase)
        )

        good_fii2 = FiiDomainFactory.build(
            ticker="GREAT11",
            p_vp=1.0,  # Valid for PVPRule
            dy_12=10.0,
            last_12_month_evaluation=20.0,
            current_month_evaluation=3.0,
            last_dividend=1.0,
            dialy_liquidity=900000,  # Above minimum 750000
            duration="indeterminada",  # Valid duration (lowercase)
        )

        await real_repository.add(good_fii1)
        await real_repository.add(good_fii2)

        result = await usecase.execute()

        assert len(result) == 2
        tickers = [fii.ticker for fii in result]
        assert "GOOD11" in tickers
        assert "GREAT11" in tickers

    @pytest.mark.asyncio
    async def test_execute_handles_empty_database(self, usecase, real_repository, clean_table):
        result = await usecase.execute()

        assert result == []
