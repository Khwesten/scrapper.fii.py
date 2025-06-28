import pytest
from unittest.mock import MagicMock
from decimal import Decimal

from app.usecases.fii_analyser_usecase import FiiAnalyserUsecase
from app.repositories.fii_repository import FiiRepository
from app.domain.fii_validator import FiiValidatorFactory
from app.domain.fii_domain import FiiDomain
from tests.factories.fii_domain_factory import FiiDomainFactory


@pytest.fixture
def mock_fii_repository():
    return MagicMock(spec=FiiRepository)


@pytest.fixture
def mock_validator_factory():
    validator_factory = MagicMock(spec=FiiValidatorFactory)
    validator_mock = MagicMock()
    validator_mock.validate.return_value = True
    validator_factory.build.return_value = validator_mock
    return validator_factory


@pytest.fixture
def analyser_usecase(mock_fii_repository, mock_validator_factory):
    return FiiAnalyserUsecase(
        fii_repository=mock_fii_repository,
        fii_validator_factory=mock_validator_factory,
        percentage=Decimal("6.0")
    )


@pytest.mark.asyncio
async def test_execute_with_tickers_returns_valid_fiis(analyser_usecase, mock_fii_repository):
    # Arrange
    good_fii = FiiDomainFactory.build(
        p_vp=Decimal("0.90"),
        dy_12=Decimal("8.0"),
        last_dividend=Decimal("1.0"),
        last_price=Decimal("100.0")
    )
    mock_fii_repository.get.return_value = good_fii
    tickers = ["TEST11"]
    
    # Act
    result = await analyser_usecase.execute(tickers=tickers)
    
    # Assert
    assert len(result) == 1
    assert result[0] == good_fii
    mock_fii_repository.get.assert_called_once_with("TEST11")


@pytest.mark.asyncio
async def test_execute_returns_all_filtered_fiis(analyser_usecase, mock_fii_repository, mock_validator_factory):
    # Arrange
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
    
    # Act
    result = await analyser_usecase.execute()
    
    # Assert
    assert len(result) == 1
    assert result[0] == good_fii
    mock_fii_repository.list.assert_called_once()
    mock_validator_factory.build.assert_called()
