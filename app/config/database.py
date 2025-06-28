import os
from typing import Optional

DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "fiis")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DYNAMODB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT")

DB_CONFIG = {
    "dynamodb": {
        "table_name": DYNAMODB_TABLE_NAME,
        "region": AWS_REGION,
        "endpoint_url": DYNAMODB_ENDPOINT,
        "local": DYNAMODB_ENDPOINT is not None
        and (
            "localhost" in DYNAMODB_ENDPOINT
            or "dynamodb-local" in DYNAMODB_ENDPOINT
            or "127.0.0.1" in DYNAMODB_ENDPOINT
        ),
    }
}


def get_db_config() -> dict:
    return DB_CONFIG["dynamodb"]


class DatabaseConfig:

    @staticmethod
    def get_aws_region() -> str:
        return AWS_REGION

    @staticmethod
    def get_dynamodb_endpoint() -> Optional[str]:
        return DYNAMODB_ENDPOINT

    @staticmethod
    def get_dynamodb_table_name() -> str:
        return DYNAMODB_TABLE_NAME

    @staticmethod
    def is_local_dynamodb() -> bool:
        endpoint = DatabaseConfig.get_dynamodb_endpoint()
        return endpoint is not None and (
            "localhost" in endpoint or "dynamodb-local" in endpoint or "127.0.0.1" in endpoint
        )

    @staticmethod
    def get_aws_credentials() -> dict:
        """Get AWS credentials from environment variables."""
        return {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region_name": DatabaseConfig.get_aws_region(),
        }

    @classmethod
    def print_config(cls) -> None:
        """Print current configuration (for debugging)."""
        print("=== Database Configuration ===")
        print(f"AWS Region: {cls.get_aws_region()}")
        print(f"DynamoDB Endpoint: {cls.get_dynamodb_endpoint()}")
        print(f"DynamoDB Table: {cls.get_dynamodb_table_name()}")
        print(f"Local DynamoDB: {cls.is_local_dynamodb()}")
        print("===============================")
