import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from app.domain.fii_validator import FiiValidator, FiiValidatorFactory
from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestFiiValidator:
    @pytest.fixture
    def mock_rule_passes(self):
        rule = MagicMock(spec=FiiRule)
        rule.validate.return_value = True
        rule.MESSAGE = "Mock rule passes"
        return rule

    @pytest.fixture
    def mock_rule_fails(self):
        rule = MagicMock(spec=FiiRule)
        rule.validate.return_value = False
        rule.MESSAGE = "Mock rule fails"
        return rule

    @pytest.fixture
    def validator_with_passing_rules(self, mock_rule_passes):
        return FiiValidator(mock_rule_passes, mock_rule_passes)

    @pytest.fixture
    def validator_with_failing_rule(self, mock_rule_passes, mock_rule_fails):
        return FiiValidator(mock_rule_passes, mock_rule_fails)

    @pytest.fixture
    def validator_empty(self):
        return FiiValidator()

    def test_validate_with_all_rules_passing(self, validator_with_passing_rules):
        fii = FiiDomainFactory.build()
        
        result = validator_with_passing_rules.validate(fii)
        
        assert result is True

    def test_validate_with_one_rule_failing(self, validator_with_failing_rule):
        fii = FiiDomainFactory.build()
        
        with patch('app.domain.fii_validator.logger') as mock_logger:
            result = validator_with_failing_rule.validate(fii)
        
        assert result is False
        mock_logger.info.assert_called_once()

    def test_validate_with_no_rules(self, validator_empty):
        fii = FiiDomainFactory.build()
        
        result = validator_empty.validate(fii)
        
        assert result is True

    def test_validate_calls_all_rules_until_failure(self, mock_rule_passes, mock_rule_fails):
        validator = FiiValidator(mock_rule_passes, mock_rule_fails, mock_rule_passes)
        fii = FiiDomainFactory.build()
        
        with patch('app.domain.fii_validator.logger'):
            result = validator.validate(fii)
        
        assert result is False
        mock_rule_passes.validate.assert_called_once_with(fii)
        mock_rule_fails.validate.assert_called_once_with(fii)

    def test_validate_with_none_fii(self, validator_with_passing_rules):
        result = validator_with_passing_rules.validate(None)
        
        assert result is True

    def test_validator_initialization_with_multiple_rules(self, mock_rule_passes, mock_rule_fails):
        validator = FiiValidator(mock_rule_passes, mock_rule_fails)
        
        assert len(validator.rules) == 2
        assert validator.rules[0] == mock_rule_passes
        assert validator.rules[1] == mock_rule_fails


class TestFiiValidatorFactory:
    def test_build_returns_validator_instance(self):
        validator = FiiValidatorFactory.build()
        
        assert isinstance(validator, FiiValidator)

    def test_build_creates_validator_with_all_rules(self):
        validator = FiiValidatorFactory.build()
        
        assert len(validator.rules) == 8

    def test_build_returns_new_instance_each_time(self):
        validator1 = FiiValidatorFactory.build()
        validator2 = FiiValidatorFactory.build()
        
        assert validator1 is not validator2

    def test_build_with_consistent_rules(self):
        validator1 = FiiValidatorFactory.build()
        validator2 = FiiValidatorFactory.build()
        
        assert len(validator1.rules) == len(validator2.rules)
