import pytest
from unittest.mock import MagicMock, AsyncMock
from decimal import Decimal

from app.usecases.fii_analyser_usecase import FiiAnalyserUsecase
from app.repositories.fii_repository import FiiRepository
from app.domain.fii_validator import FiiValidatorFactory
from app.domain.fii_domain import FiiDomain
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiAnalyserUsecase:
    @pytest.fixture
    def mock_fii_repository(self):
        return MagicMock(spec=FiiRepository)

    @pytest.fixture
    def mock_validator_factory(self):
        validator_factory = MagicMock(spec=FiiValidatorFactory)
        validator_mock = MagicMock()
        validator_mock.validate.return_value = True
        validator_factory.build.return_value = validator_mock
        return validator_factory

    @pytest.fixture
    def analyser_usecase(self, mock_fii_repository, mock_validator_factory):
        return FiiAnalyserUsecase(
            fii_repository=mock_fii_repository,
            fii_validator_factory=mock_validator_factory,
            percentage=Decimal("6.0")
        )

    @pytest.mark.asyncio
    async def test_execute_with_tickers_returns_valid_fiis(self, analyser_usecase, mock_fii_repository):
        good_fii = FiiDomainFactory.build(
            p_vp=Decimal("0.90"),
            dy_12=Decimal("8.0"),
            last_dividend=Decimal("1.0"),
            last_price=Decimal("100.0")
        )
        mock_fii_repository.get.return_value = good_fii
        tickers = ["TEST11"]
        
        result = await analyser_usecase.execute(tickers=tickers)
        
        assert len(result) == 1
        assert result[0] == good_fii
        mock_fii_repository.get.assert_called_once_with("TEST11")

    @pytest.mark.asyncio
    async def test_execute_with_tickers_filters_invalid_dy(self, analyser_usecase, mock_fii_repository):
        bad_fii = FiiDomainFactory.build(
            dy_12=Decimal("3.0"),
            last_dividend=Decimal("1.0"),
            last_price=Decimal("100.0")
        )
        mock_fii_repository.get.return_value = bad_fii
        tickers = ["TEST11"]
        
        result = await analyser_usecase.execute(tickers=tickers)
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_execute_with_tickers_filters_zero_dividend(self, analyser_usecase, mock_fii_repository):
        bad_fii = FiiDomainFactory.build(
            dy_12=Decimal("8.0"),
            last_dividend=Decimal("0.0"),
            last_price=Decimal("100.0")
        )
        mock_fii_repository.get.return_value = bad_fii
        tickers = ["TEST11"]
        
        result = await analyser_usecase.execute(tickers=tickers)
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_execute_with_tickers_filters_zero_price(self, analyser_usecase, mock_fii_repository):
        bad_fii = FiiDomainFactory.build(
            dy_12=Decimal("8.0"),
            last_dividend=Decimal("1.0"),
            last_price=Decimal("0.0")
        )
        mock_fii_repository.get.return_value = bad_fii
        tickers = ["TEST11"]
        
        result = await analyser_usecase.execute(tickers=tickers)
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_execute_with_tickers_filters_invalid_validation(self, analyser_usecase, mock_fii_repository, mock_validator_factory):
        bad_fii = FiiDomainFactory.build(
            dy_12=Decimal("8.0"),
            last_dividend=Decimal("1.0"),
            last_price=Decimal("100.0")
        )
        mock_fii_repository.get.return_value = bad_fii
        mock_validator_factory.build.return_value.validate.return_value = False
        tickers = ["TEST11"]
        
        result = await analyser_usecase.execute(tickers=tickers)
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_execute_with_tickers_handles_none_fii(self, analyser_usecase, mock_fii_repository):
        mock_fii_repository.get.return_value = None
        tickers = ["INVALID"]
        
        result = await analyser_usecase.execute(tickers=tickers)
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_execute_returns_all_filtered_fiis(self, analyser_usecase, mock_fii_repository, mock_validator_factory):
        good_fii = FiiDomainFactory.build(
            dy_12=Decimal("8.0"),
            last_dividend=Decimal("1.0"),
            last_price=Decimal("100.0")
        )
        bad_fii = FiiDomainFactory.build(
            dy_12=Decimal("3.0"),
            last_dividend=Decimal("1.0"),
            last_price=Decimal("100.0")
        )
        mock_fii_repository.list.return_value = [good_fii, bad_fii]
        
        result = await analyser_usecase.execute()
        
        assert len(result) == 1
        assert result[0] == good_fii
        mock_fii_repository.list.assert_called_once()
        mock_validator_factory.build.assert_called()

    @pytest.mark.asyncio
    async def test_execute_filters_all_invalid_fiis(self, analyser_usecase, mock_fii_repository, mock_validator_factory):
        bad_fii1 = FiiDomainFactory.build(dy_12=Decimal("3.0"))
        bad_fii2 = FiiDomainFactory.build(last_dividend=Decimal("0.0"))
        mock_fii_repository.list.return_value = [bad_fii1, bad_fii2]
        
        result = await analyser_usecase.execute()
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_execute_with_empty_repository(self, analyser_usecase, mock_fii_repository):
        mock_fii_repository.list.return_value = []
        
        result = await analyser_usecase.execute()
        
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_with_valid_fii(self, analyser_usecase, mock_fii_repository):
        good_fii = FiiDomainFactory.build(
            dy_12=Decimal("8.0"),
            last_dividend=Decimal("1.0"),
            last_price=Decimal("100.0")
        )
        mock_fii_repository.get.return_value = good_fii
        
        result = await analyser_usecase._get("TEST11")
        
        assert result == good_fii

    @pytest.mark.asyncio
    async def test_get_with_invalid_fii(self, analyser_usecase, mock_fii_repository):
        bad_fii = FiiDomainFactory.build(dy_12=Decimal("3.0"))
        mock_fii_repository.get.return_value = bad_fii
        
        result = await analyser_usecase._get("TEST11")
        
        assert result is None
