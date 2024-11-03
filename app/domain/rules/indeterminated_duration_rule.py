from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class IndeterminatedDurationRule(FiiRule):
    INDETERMINADO = "indeterminado"
    INDETERMINADA = "indeterminada"
    MESSAGE = f"Duration is not indeterminated"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        return fii.duration in [cls.INDETERMINADO, cls.INDETERMINADA]
