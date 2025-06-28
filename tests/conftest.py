from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from conftest import *  # Import global fixtures if available


# Global fixtures to consolidate common mocks
@pytest.fixture
def fii_domain_sample():
    from tests.factories.fii_domain_factory import FiiDomainFactory

    return FiiDomainFactory.build(
        ticker="SAMPLE11",
        p_vp=Decimal("0.95"),
        dy_12=Decimal("8.5"),
        last_dividend=Decimal("1.20"),
        last_price=Decimal("100.0"),
        dialy_liquidity=Decimal("50000"),
    )


@pytest.fixture
def mock_repository_empty():
    from app.repositories.fii_repository import FiiRepository

    repository = MagicMock(spec=FiiRepository)
    repository.list.return_value = []
    repository.get.return_value = None
    repository.add.return_value = 1
    return repository


@pytest.fixture
def mock_gateway():
    from unittest.mock import AsyncMock

    from app.gateways.status_invest_gateway import FiiGateway

    gateway = MagicMock(spec=FiiGateway)
    gateway.list = AsyncMock(return_value=["TEST11", "TEST12"])
    gateway.get = AsyncMock()
    gateway.close = AsyncMock()
    return gateway


# Fixture to mock external dependencies globally
@pytest.fixture(autouse=True)
def mock_external_deps():
    with patch("app.repositories.fii_repository_factory.FiiRepositoryFactory.create") as mock_factory:
        mock_factory.return_value = MagicMock()
        yield mock_factory
