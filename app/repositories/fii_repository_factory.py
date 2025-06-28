from app.repositories.fii_repository import FiiRepository
from app.repositories.fii_dynamodb_repository import FiiDynamoDBRepository


class FiiRepositoryFactory:
    
    @staticmethod
    def create() -> FiiRepository:
        return FiiDynamoDBRepository()
