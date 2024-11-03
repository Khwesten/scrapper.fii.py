from app.domain.fii_domain import FiiDomain
from app.domain.rules.fii_rule import FiiRule


class PVPRule(FiiRule):
    MAX_P_VPA = 1.1
    MIN_P_VPA = 0.9
    MESSAGE = f"PVP is not in: {MIN_P_VPA} <= p_vp >= {MAX_P_VPA}"

    @classmethod
    def validate(cls, fii: FiiDomain) -> bool:
        return fii.p_vp >= cls.MIN_P_VPA and fii.p_vp <= cls.MAX_P_VPA
