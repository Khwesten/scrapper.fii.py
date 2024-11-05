from app.domain.fii_domain import FiiDomain


class FiiRule:
    MESSAGE: str = None

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool: ...
