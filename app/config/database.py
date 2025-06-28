from typing import Optional

from app_config import AppConfig

config = AppConfig()

DYNAMODB_TABLE_NAME = config.dynamodb_table_name
AWS_REGION = config.dynamodb_region
DYNAMODB_ENDPOINT = config.dynamodb_endpoint

DB_CONFIG = {
    "dynamodb": {
        "table_name": DYNAMODB_TABLE_NAME,
        "region": AWS_REGION,
        "endpoint_url": DYNAMODB_ENDPOINT,
        "local": config.is_local_dynamodb,
    }
}


def get_db_config() -> dict:
    return DB_CONFIG["dynamodb"]


class DatabaseConfig:

    @staticmethod
    def get_aws_region() -> str:
        return config.dynamodb_region

    @staticmethod
    def get_dynamodb_endpoint() -> Optional[str]:
        return config.dynamodb_endpoint

    @staticmethod
    def get_dynamodb_table_name() -> str:
        return config.dynamodb_table_name

    @staticmethod
    def is_local_dynamodb() -> bool:
        return config.is_local_dynamodb

    @staticmethod
    def get_aws_credentials() -> dict:
        return config.get_dynamodb_credentials()

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)."""
        print("=== Database Configuration ===")
        print(f"AWS Region: {cls.get_aws_region()}")
        print(f"DynamoDB Endpoint: {cls.get_dynamodb_endpoint()}")
        print(f"DynamoDB Table: {cls.get_dynamodb_table_name()}")
        print(f"Local DynamoDB: {cls.is_local_dynamodb()}")
        print("===============================")
