from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository
from app.repositories.fii_repository import FiiRepository


class FiiRepositoryFactory:

    @staticmethod
    def create() -> FiiRepository:
        return FiiDynamoDBRepository()
