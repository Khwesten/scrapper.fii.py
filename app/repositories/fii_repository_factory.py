import asyncio
from typing import Optional

from app.libs.logger import logger
from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository
from app.repositories.fii_memory_repository import FiiMemoryRepository
from app.repositories.fii_repository import FiiRepository


class FiiRepositoryFactory:
    _cached_repository: Optional[FiiRepository] = None
    _cache_tested = False

    @classmethod
    def create(cls) -> FiiRepository:
        if cls._cached_repository is None:
            cls._cached_repository = cls._create_with_fallback()
        return cls._cached_repository

    @classmethod
    def _create_with_fallback(cls) -> FiiRepository:
        try:
            dynamodb_repo = FiiDynamoDBRepository()
            logger.info("Created DynamoDB repository, will test on first use")
            return cls._create_tested_repository(dynamodb_repo)

        except Exception as e:
            logger.error(f"Failed to create DynamoDB repository: {e}, using memory repository")
            return FiiMemoryRepository()

    @classmethod
    def _create_tested_repository(cls, dynamodb_repo: FiiDynamoDBRepository) -> FiiRepository:
        """Returns a repository that tests DynamoDB on first use and falls back to memory if needed"""

        class TestingRepository(FiiRepository):
            def __init__(self):
                self._actual_repo = None
                self._tested = False

            async def _get_repo(self):
                if not self._tested:
                    try:
                        await asyncio.wait_for(dynamodb_repo.list(), timeout=3.0)
                        self._actual_repo = dynamodb_repo
                        logger.info("DynamoDB repository test successful")
                    except Exception as e:
                        logger.warning(f"DynamoDB test failed: {e}, falling back to memory repository")
                        self._actual_repo = FiiMemoryRepository()
                    self._tested = True
                return self._actual_repo

            async def list(self):
                repo = await self._get_repo()
                return await repo.list()

            async def save(self, fii):
                repo = await self._get_repo()
                return await repo.save(fii)

            async def get_by_ticker(self, ticker):
                repo = await self._get_repo()
                return await repo.get_by_ticker(ticker)

            async def save_all(self, fiis):
                repo = await self._get_repo()
                return await repo.save_all(fiis)

            async def add(self, fii):
                repo = await self._get_repo()
                return await repo.add(fii)

            async def get(self, ticker):
                repo = await self._get_repo()
                return await repo.get(ticker)

        return TestingRepository()
