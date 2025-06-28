from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest



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
    from app.gateways.status_invest_gateway import FiiGateway

    gateway = MagicMock(spec=FiiGateway)
    gateway.list = AsyncMock(return_value=["TEST11", "TEST12"])
    gateway.get = AsyncMock()
    gateway.close = AsyncMock()
    return gateway


# Mock DynamoDB repository for unit tests
@pytest.fixture
def mock_dynamodb_repository():
    from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository

    repository = MagicMock(spec=FiiDynamoDBRepository)
    repository.add = AsyncMock(return_value=None)
    repository.get = AsyncMock(return_value=None)
    repository.list = AsyncMock(return_value=[])
    repository.update = AsyncMock(return_value=None)
    return repository


# Real repository fixture for integration tests only
@pytest.fixture
def real_repository(dynamodb_test_config):
    from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository
    from app_config import AppConfig

    config = AppConfig()
    return FiiDynamoDBRepository(config.dynamodb_table_name)
