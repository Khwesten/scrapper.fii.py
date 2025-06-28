import os
from pathlib import Path
from typing import Dict, Optional

import yaml

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))


class AppConfig:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._config = self._load_config()

    def _load_config(self) -> Dict:
        env = os.getenv("ENVIRONMENT", "local")

        # First try to load from YAML for the specific environment
        config_path = Path(__file__).parent / f"config-{env}.yml"

        if not config_path.exists():
            config_path = Path(__file__).parent / "config.yml"

        if config_path.exists():
            return self._load_from_yaml(config_path)
        else:
            # Fall back to environment variables if no YAML file found
            return self._load_from_env()

    def _load_from_yaml(self, config_path: Path = None) -> Dict:
        if config_path is None:
            config_path = Path(__file__).parent / f"config-{os.getenv('ENVIRONMENT', 'local')}.yml"

            if not config_path.exists():
                config_path = Path(__file__).parent / "config.yml"

        if config_path.exists():
            with open(config_path, "r") as file:
                return yaml.safe_load(file)
        else:
            return self._load_from_env()

    def _load_from_env(self) -> Dict:
        return {
            "api": {
                "host": os.getenv("API_HOST", "0.0.0.0"),
                "port": int(os.getenv("API_PORT", "8000")),
                "debug": os.getenv("API_DEBUG", "false").lower() == "true",
            },
            "database": {
                "type": os.getenv("FII_REPOSITORY_TYPE", "dynamodb"),
                "dynamodb": {
                    "table_name": os.getenv("DYNAMODB_TABLE_NAME", "fiis"),
                    "region": os.getenv("AWS_REGION", "us-east-1"),
                    "endpoint": os.getenv("DYNAMODB_ENDPOINT"),
                    "access_key": os.getenv("AWS_ACCESS_KEY_ID"),
                    "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
                },
            },
            "external": {
                "status_invest": {
                    "base_url": os.getenv("STATUS_INVEST_BASE_URL", "https://statusinvest.com.br/fundos-imobiliarios/"),
                    "timeout": int(os.getenv("STATUS_INVEST_TIMEOUT", "30")),
                }
            },
            "scheduler": {"scrape_interval_hours": int(os.getenv("SCRAPE_INTERVAL_HOURS", "8"))},
        }

    @property
    def api_host(self) -> str:
        return self._config["api"]["host"]

    @property
    def api_port(self) -> int:
        return self._config["api"]["port"]

    @property
    def api_debug(self) -> bool:
        return self._config["api"]["debug"]

    @property
    def db_type(self) -> str:
        return self._config["database"]["type"]

    @property
    def dynamodb_table_name(self) -> str:
        return self._config["database"]["dynamodb"]["table_name"]

    @property
    def dynamodb_region(self) -> str:
        return self._config["database"]["dynamodb"]["region"]

    @property
    def dynamodb_endpoint(self) -> Optional[str]:
        return self._config["database"]["dynamodb"]["endpoint"]

    @property
    def dynamodb_access_key(self) -> Optional[str]:
        return self._config["database"]["dynamodb"]["access_key"]

    @property
    def dynamodb_secret_key(self) -> Optional[str]:
        return self._config["database"]["dynamodb"]["secret_key"]

    @property
    def status_invest_base_url(self) -> str:
        return self._config["external"]["status_invest"]["base_url"]

    @property
    def status_invest_timeout(self) -> int:
        return self._config["external"]["status_invest"]["timeout"]

    @property
    def scrape_interval_hours(self) -> int:
        return self._config["scheduler"]["scrape_interval_hours"]

    @property
    def is_local_dynamodb(self) -> bool:
        endpoint = self.dynamodb_endpoint
        return endpoint is not None and (
            "localhost" in endpoint or "dynamodb-local" in endpoint or "127.0.0.1" in endpoint
        )

    def get_dynamodb_credentials(self) -> Dict:
        return {
            "aws_access_key_id": self.dynamodb_access_key,
            "aws_secret_access_key": self.dynamodb_secret_key,
            "region_name": self.dynamodb_region,
        }
