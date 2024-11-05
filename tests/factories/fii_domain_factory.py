import factory

from app.domain.fii_domain import FiiDomain


class FiiDomainFactory(factory.Factory):
    class Meta:
        model = FiiDomain

    ticker = factory.Faker("bothify", text="????11")
    p_vp = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    segment = factory.Faker("word", ext_word_list=["Shoppings", "Logística", "Híbrido"])
    duration = factory.Faker("word", ext_word_list=["Indeterminada", "Indeterminado", "brubles"])
    last_12_month_evaluation = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    current_month_evaluation = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    last_price = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    last_dividend = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    dy_12 = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    dialy_liquidity = factory.Faker("pydecimal", left_digits=2, right_digits=2, positive=True)
    start_date = None
