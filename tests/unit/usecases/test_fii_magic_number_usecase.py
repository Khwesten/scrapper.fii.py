from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.repositories.fii_repository import FiiRepository
from app.usecases.fii_magic_number_usecase import (
    FiiMagicNumberUseCase,
    MagicNumberResponse,
)
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiMagicNumberUseCase:
    @pytest.fixture
    def mock_fii_repository(self):
        return MagicMock(spec=FiiRepository)

    @pytest.fixture
    def magic_number_usecase(self, mock_fii_repository):
        return FiiMagicNumberUseCase(fii_repository=mock_fii_repository, invested_value=10000)

    @pytest.fixture
    def magic_number_usecase_default_value(self, mock_fii_repository):
        return FiiMagicNumberUseCase(fii_repository=mock_fii_repository)

    @pytest.mark.asyncio
    async def test_execute_with_valid_fiis(self, magic_number_usecase, mock_fii_repository):
        fii1 = FiiDomainFactory.build(ticker="TEST11", last_price=Decimal("100.0"), last_dividend=Decimal("10.0"))
        fii2 = FiiDomainFactory.build(ticker="TEST12", last_price=Decimal("120.0"), last_dividend=Decimal("8.0"))

        mock_fii_repository.list.return_value = [fii1, fii2]

        result = await magic_number_usecase.execute()

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(item, MagicNumberResponse) for item in result)
        assert result[0].ticker == "TEST11"
        assert result[1].ticker == "TEST12"
        mock_fii_repository.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_empty_repository(self, magic_number_usecase, mock_fii_repository):
        mock_fii_repository.list.return_value = []

        result = await magic_number_usecase.execute()

        assert result == []
        mock_fii_repository.list.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_single_fii(self, magic_number_usecase, mock_fii_repository):
        fii = FiiDomainFactory.build(ticker="TEST11", last_price=Decimal("100.0"), last_dividend=Decimal("10.0"))
        mock_fii_repository.list.return_value = [fii]

        result = await magic_number_usecase.execute()

        assert len(result) == 1
        assert result[0].ticker == "TEST11"

    def test_calculate_magic_number(self):
        usecase = FiiMagicNumberUseCase(invested_value=10000)
        fii = FiiDomainFactory.build(ticker="TEST11", last_price=Decimal("100.0"), last_dividend=Decimal("10.0"))

        result = usecase._calculate_magic_number(fii)

        assert result.ticker == "TEST11"
        assert result.magic_number == 10
        assert result.quotas_for_invested_value == 100
        assert result.dividend_for_invested_value == Decimal("1000.0")
        assert result.invested_value == 10000

    def test_calculate_magic_number_with_fractional_values(self):
        usecase = FiiMagicNumberUseCase(invested_value=15000)
        fii = FiiDomainFactory.build(ticker="TEST11", last_price=Decimal("120.5"), last_dividend=Decimal("8.25"))

        result = usecase._calculate_magic_number(fii)

        assert result.ticker == "TEST11"
        assert result.magic_number == 14
        assert result.quotas_for_invested_value == 124
        assert result.dividend_for_invested_value == Decimal("1023.0")
        assert result.invested_value == 15000

    def test_calculate_magic_number_with_zero_dividend(self):
        usecase = FiiMagicNumberUseCase(invested_value=10000)
        fii = FiiDomainFactory.build(ticker="TEST11", last_price=Decimal("100.0"), last_dividend=Decimal("0.01"))

        result = usecase._calculate_magic_number(fii)

        assert result.magic_number == 10000

    def test_calculate_magic_number_with_high_price(self):
        usecase = FiiMagicNumberUseCase(invested_value=1000)
        fii = FiiDomainFactory.build(ticker="TEST11", last_price=Decimal("2000.0"), last_dividend=Decimal("100.0"))

        result = usecase._calculate_magic_number(fii)

        assert result.quotas_for_invested_value == 0
        assert result.dividend_for_invested_value == Decimal("0.0")

    def test_default_invested_value(self, magic_number_usecase_default_value):
        assert magic_number_usecase_default_value.invested_value == 10000

    def test_custom_invested_value(self, magic_number_usecase):
        assert magic_number_usecase.invested_value == 10000
