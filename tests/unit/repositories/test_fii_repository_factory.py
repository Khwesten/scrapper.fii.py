import pytest

from app.repositories.fii_repository_factory import FiiRepositoryFactory


class TestFiiRepositoryFactory:
    def test_factory_is_static_method(self):
        assert callable(FiiRepositoryFactory.create)

    def test_factory_does_not_require_instance(self):
        repository = FiiRepositoryFactory.create()
        
        assert repository is not None

    def test_factory_create_method_exists(self):
        assert hasattr(FiiRepositoryFactory, 'create')

    def test_factory_returns_something(self):
        result = FiiRepositoryFactory.create()
        
        assert result is not None
