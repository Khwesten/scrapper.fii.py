import os

import pytest

from app_config import AppConfig


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configure test environment based on ENVIRONMENT var"""
    # Force test environment if running pytest
    if not os.getenv("ENVIRONMENT"):
        os.environ["ENVIRONMENT"] = "test"

    # Reload config to pick up environment changes
    AppConfig._instance = None
    AppConfig._config = None

    yield


@pytest.fixture(scope="function")
def dynamodb_test_config():
    """Setup DynamoDB config for integration tests - only for real DynamoDB"""
    config = AppConfig()

    # Only support real DynamoDB for integration tests
    if config.dynamodb_endpoint and config.dynamodb_endpoint != "mock":
        yield _ensure_real_dynamodb_table(config)
    else:
        pytest.skip("DynamoDB endpoint not configured for integration tests")


def _ensure_real_dynamodb_table(config):
    """Ensure real DynamoDB table exists for integration tests"""
    import boto3
    from botocore.exceptions import ClientError

    # Get credentials from config
    creds = config.get_dynamodb_credentials()

    dynamodb = boto3.resource("dynamodb", endpoint_url=config.dynamodb_endpoint, **creds)

    try:
        table = dynamodb.Table(config.dynamodb_table_name)
        table.load()
        return table
    except ClientError:
        # Create table if it doesn't exist
        table = dynamodb.create_table(
            TableName=config.dynamodb_table_name,
            KeySchema=[{"AttributeName": "ticker", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "ticker", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        return table


@pytest.fixture
def clean_dynamodb_table(dynamodb_test_config):
    """Clean DynamoDB table after each test"""
    table = dynamodb_test_config
    yield table

    # Clean up table contents
    try:
        scan = table.scan()
        with table.batch_writer() as batch:
            for item in scan.get("Items", []):
                batch.delete_item(Key={"ticker": item["ticker"]})
    except Exception:
        pass  # Ignore cleanup errors
