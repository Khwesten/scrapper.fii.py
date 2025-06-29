from decimal import Decimal

from app.domain.fii_domain import FiiDomain
from app.usecases.fii_analyser_usecase import FiiAnalyserUsecase


class TestFiiAnalyserUsecaseAdditional:
    """Additional integration tests for FiiAnalyserUsecase to increase coverage"""

    async def test_execute_with_tickers_includes_invalid_fiis(self, clean_dynamodb_table):
        """Test execute with tickers parameter when some FIIs are invalid"""
        # Create test FIIs with different validity conditions
        valid_fii = FiiDomain(
            ticker="VALID11",
            p_vp=Decimal("0.95"),
            last_dividend=Decimal("0.50"),
            segment="shopping",
            last_12_month_evaluation=Decimal("5.0"),
            current_month_evaluation=Decimal("1.0"),
            last_price=Decimal("100.00"),
            start_date=None,
            dy_12=Decimal("8.0"),  # Above default 6%
            duration="indeterminado",
            dialy_liquidity=Decimal("1000000"),
        )

        invalid_fii = FiiDomain(
            ticker="INVALID11",
            p_vp=Decimal("1.5"),  # Invalid P/VP > 1.2
            last_dividend=Decimal("0.50"),
            segment="shopping",
            last_12_month_evaluation=Decimal("5.0"),
            current_month_evaluation=Decimal("1.0"),
            last_price=Decimal("100.00"),
            start_date=None,
            dy_12=Decimal("8.0"),
            duration="indeterminado",
            dialy_liquidity=Decimal("1000000"),
        )

        usecase = FiiAnalyserUsecase()

        # Save test FIIs
        await usecase.fii_repository.add(valid_fii)
        await usecase.fii_repository.add(invalid_fii)

        # Execute with specific tickers
        result = await usecase.execute(tickers=["VALID11", "INVALID11"])

        # Should only return the valid FII
        assert len(result) == 1
        assert result[0].ticker == "VALID11"

    async def test_execute_with_tickers_handles_nonexistent_fiis(self, clean_dynamodb_table):
        """Test execute with tickers parameter when some FIIs don't exist"""
        # Create one valid FII
        valid_fii = FiiDomain(
            ticker="EXISTS11",
            p_vp=Decimal("0.95"),
            last_dividend=Decimal("0.50"),
            segment="shopping",
            last_12_month_evaluation=Decimal("5.0"),
            current_month_evaluation=Decimal("1.0"),
            last_price=Decimal("100.00"),
            start_date=None,
            dy_12=Decimal("8.0"),
            duration="indeterminado",
            dialy_liquidity=Decimal("1000000"),
        )

        usecase = FiiAnalyserUsecase()
        await usecase.fii_repository.add(valid_fii)

        # Execute with both existing and non-existing tickers
        result = await usecase.execute(tickers=["EXISTS11", "NOTEXISTS11"])

        # Should only return the existing valid FII
        assert len(result) == 1
        assert result[0].ticker == "EXISTS11"

    async def test_execute_with_low_dy_fiis(self, clean_dynamodb_table):
        """Test execute excludes FIIs with DY below threshold"""
        # Create FII with low DY
        low_dy_fii = FiiDomain(
            ticker="LOWDY11",
            p_vp=Decimal("0.95"),
            last_dividend=Decimal("0.50"),
            segment="shopping",
            last_12_month_evaluation=Decimal("5.0"),
            current_month_evaluation=Decimal("1.0"),
            last_price=Decimal("100.00"),
            start_date=None,
            dy_12=Decimal("4.0"),  # Below default 6%
            duration="indeterminado",
            dialy_liquidity=Decimal("1000000"),
        )

        usecase = FiiAnalyserUsecase()
        await usecase.fii_repository.add(low_dy_fii)

        result = await usecase.execute()

        # Should return empty list since DY is below threshold
        assert len(result) == 0

    async def test_execute_with_zero_dividend_fiis(self, clean_dynamodb_table):
        """Test execute excludes FIIs with zero dividend"""
        # Create FII with zero dividend
        zero_dividend_fii = FiiDomain(
            ticker="ZERODIV11",
            p_vp=Decimal("0.95"),
            last_dividend=Decimal("0.00"),  # Zero dividend
            segment="shopping",
            last_12_month_evaluation=Decimal("5.0"),
            current_month_evaluation=Decimal("1.0"),
            last_price=Decimal("100.00"),
            start_date=None,
            dy_12=Decimal("8.0"),
            duration="indeterminado",
            dialy_liquidity=Decimal("1000000"),
        )

        usecase = FiiAnalyserUsecase()
        await usecase.fii_repository.add(zero_dividend_fii)

        result = await usecase.execute()

        # Should return empty list since dividend is zero
        assert len(result) == 0

    async def test_execute_with_zero_price_fiis(self, clean_dynamodb_table):
        """Test execute excludes FIIs with zero price"""
        # Create FII with zero price
        zero_price_fii = FiiDomain(
            ticker="ZEROPRICE11",
            p_vp=Decimal("0.95"),
            last_dividend=Decimal("0.50"),
            segment="shopping",
            last_12_month_evaluation=Decimal("5.0"),
            current_month_evaluation=Decimal("1.0"),
            last_price=Decimal("0.00"),  # Zero price
            start_date=None,
            dy_12=Decimal("8.0"),
            duration="indeterminado",
            dialy_liquidity=Decimal("1000000"),
        )

        usecase = FiiAnalyserUsecase()
        await usecase.fii_repository.add(zero_price_fii)

        result = await usecase.execute()

        # Should return empty list since price is zero
        assert len(result) == 0

    async def test_get_returns_none_for_invalid_fii(self, clean_dynamodb_table):
        """Test _get method returns None for invalid FII"""
        # Create invalid FII
        invalid_fii = FiiDomain(
            ticker="INVALID11",
            p_vp=Decimal("1.5"),  # Invalid P/VP > 1.2
            last_dividend=Decimal("0.50"),
            segment="shopping",
            last_12_month_evaluation=Decimal("5.0"),
            current_month_evaluation=Decimal("1.0"),
            last_price=Decimal("100.00"),
            start_date=None,
            dy_12=Decimal("8.0"),
            duration="indeterminado",
            dialy_liquidity=Decimal("1000000"),
        )

        usecase = FiiAnalyserUsecase()
        await usecase.fii_repository.add(invalid_fii)

        result = await usecase._get("INVALID11")

        # Should return None since FII is invalid
        assert result is None
