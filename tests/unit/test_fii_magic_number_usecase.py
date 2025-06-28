import pytest
from unittest.mock import MagicMock
from decimal import Decimal

from app.usecases.fii_magic_number_usecase import FiiMagicNumberUseCase, MagicNumberResponse
from app.repositories.fii_repository import FiiRepository
from tests.factories.fii_domain_factory import FiiDomainFactory


@pytest.fixture
def mock_fii_repository():
    return MagicMock(spec=FiiRepository)


@pytest.fixture
def magic_number_usecase(mock_fii_repository):
    return FiiMagicNumberUseCase(fii_repository=mock_fii_repository, invested_value=10000)


@pytest.mark.asyncio
async def test_execute_with_valid_fiis(magic_number_usecase, mock_fii_repository):
    # Arrange
    fii1 = FiiDomainFactory.build(
        ticker="TEST11",
        last_price=Decimal("100.0"),
        last_dividend=Decimal("10.0")
    )
    fii2 = FiiDomainFactory.build(
        ticker="TEST12",
        last_price=Decimal("120.0"),
        last_dividend=Decimal("8.0")
    )
    
    mock_fii_repository.list.return_value = [fii1, fii2]
    
    # Act
    result = await magic_number_usecase.execute()
    
    # Assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(isinstance(item, MagicNumberResponse) for item in result)
    assert result[0].ticker == "TEST11"
    assert result[1].ticker == "TEST12"
    mock_fii_repository.list.assert_called_once()


@pytest.mark.asyncio
async def test_execute_with_empty_repository(magic_number_usecase, mock_fii_repository):
    # Arrange
    mock_fii_repository.list.return_value = []
    
    # Act
    result = await magic_number_usecase.execute()
    
    # Assert
    assert result == []
    mock_fii_repository.list.assert_called_once()


def test_calculate_magic_number():
    # Arrange
    usecase = FiiMagicNumberUseCase(invested_value=10000)
    fii = FiiDomainFactory.build(
        ticker="TEST11",
        last_price=Decimal("100.0"),
        last_dividend=Decimal("10.0")
    )
    
    # Act
    result = usecase._calculate_magic_number(fii)
    
    # Assert
    assert result.ticker == "TEST11"
    assert result.magic_number == 10
    assert result.quotas_for_invested_value == 100
    assert result.dividend_for_invested_value == Decimal("1000.0")
    assert result.invested_value == 10000
