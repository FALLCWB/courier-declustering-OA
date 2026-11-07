"""Published dispatch models of Part 1 (untrained). Each has `assign(view) -> [(order, courier), ...]`."""
from models.auad_holding import AuadHolding
from models.backpressure import MirrorBackpressure
from models.foodmatch import FoodMatch
from models.forecast_aware import ForecastAware
from models.jahanshahi_dqn import JahanshahiDQN
from models.li_meanfield import LiMeanField
from models.xu_value import XuValue
from models.stay import StayPolicy
from models.zhu_coverage import ZhuCoverage

MODELS = {"foodmatch": FoodMatch, "forecast": ForecastAware, "backpressure": MirrorBackpressure, "xu": XuValue, "jahanshahi": JahanshahiDQN, "li": LiMeanField, "zhu": ZhuCoverage, "auad": AuadHolding, "jusup": None, "stay": StayPolicy}


def _jusup(**kw):
    """Imported on use: torch is in the FE-SIM-1 environment only."""
    from models.jusup_mf import JusupMF
    return JusupMF(**kw)


MODELS["jusup"] = _jusup
