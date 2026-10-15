"""Pure inventory math. No I/O. Used by the tools AND by the validator."""
import math
from . import config


def cents(x):
    return int(round(x * 100))


def floor_pack(q, pack):
    return (int(q) // pack) * pack


def ceil_pack(q, pack):
    return -(-int(q) // pack) * pack


def demand_assessment(forecast, history):
    """Decide whether recent sales really differ from the forecast.

    sustained_surge  -> trust recent sales (>=30% above forecast on >=5 of last 7 days)
    single_day_spike -> ignore it, probably an outlier / data error
    ambiguous        -> 3-4 elevated days, keep forecast but flag it
    normal           -> keep forecast
    """
    last7 = history[-7:]
    avg7 = sum(last7) / len(last7)
    ratio = avg7 / forecast if forecast else 1.0
    elevated = sum(1 for d in last7 if d >= forecast * 1.2)
    effective = forecast
    if ratio >= 1.3 and elevated >= 5:
        status, effective = "sustained_surge", math.ceil(avg7)
    elif ratio >= 1.3 and elevated <= 2:
        status = "single_day_spike"
    elif ratio >= 1.3:
        status = "ambiguous"
    else:
        status = "normal"
    return {
        "status": status,
        "effective_daily": effective,
        "forecast_daily": forecast,
        "avg_last_7": round(avg7, 1),
        "ratio_vs_forecast": round(ratio, 2),
        "elevated_days_of_7": elevated,
        "peak_day": max(last7),
    }


def target_position(daily, lead_days, safety):
    """Stock (on hand + incoming) we want to hold when placing an order today."""
    return math.ceil(daily * (lead_days + config.REVIEW_PERIOD_DAYS) + safety)


def max_cover(target):
    return math.floor(config.MAX_COVER_FACTOR * target)
