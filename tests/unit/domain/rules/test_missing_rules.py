from app.domain.rules.daily_liquidity_rule import DailyLiquidityRule
from app.domain.rules.minimum_dy_rule import MinimumDyRule
from app.domain.rules.old_than_rule import OldThanRule
from tests.factories.fii_domain_factory import FiiDomainFactory


class TestDailyLiquidityRule:

    def test_valid_fii_with_high_liquidity(self):
        fii = FiiDomainFactory.build(dialy_liquidity=800000)

        result = DailyLiquidityRule.validate(fii)

        assert result is True

    def test_invalid_fii_with_low_liquidity(self):
        fii = FiiDomainFactory.build(dialy_liquidity=500000)

        result = DailyLiquidityRule.validate(fii)

        assert result is False

    def test_invalid_fii_with_none_liquidity(self):
        fii = FiiDomainFactory.build(dialy_liquidity=None)

        result = DailyLiquidityRule.validate(fii)

        assert result is True


class TestMinimumDyRule:

    def test_valid_fii_with_high_dy(self):
        fii = FiiDomainFactory.build(dy_12=8.5)

        result = MinimumDyRule.validate(fii)

        assert result is True

    def test_invalid_fii_with_low_dy(self):
        fii = FiiDomainFactory.build(dy_12=4.5)

        result = MinimumDyRule.validate(fii)

        assert result is False

    def test_invalid_fii_with_none_dy(self):
        # Criar FII com dy_12 válido primeiro, depois setar None manualmente
        fii = FiiDomainFactory.build(dy_12=8.0)
        fii.dy_12 = None

        result = MinimumDyRule.validate(fii)

        assert result is False


class TestOldThanRule:

    def test_valid_fii_with_old_start_date(self):
        from datetime import date, timedelta

        old_date = date.today() - timedelta(days=800)
        fii = FiiDomainFactory.build(start_date=old_date)

        result = OldThanRule.validate(fii)

        assert result is True

    def test_invalid_fii_with_recent_start_date(self):
        from datetime import date, timedelta

        recent_date = date.today() - timedelta(days=100)
        fii = FiiDomainFactory.build(start_date=recent_date)

        result = OldThanRule.validate(fii)

        assert result is False

    def test_invalid_fii_with_none_start_date(self):
        fii = FiiDomainFactory.build(start_date=None)

        result = OldThanRule.validate(fii)

        assert result is True

    def test_invalid_fii_with_future_start_date(self):
        from datetime import date, timedelta

        future_date = date.today() + timedelta(days=100)
        fii = FiiDomainFactory.build(start_date=future_date)

        result = OldThanRule.validate(fii)

        assert result is False
