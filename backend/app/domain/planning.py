"""Pure inventory math. No database, no network. Used by tools AND validator."""
import math
from app.core.policy import policy


def demand_assessment(forecast, history):
    """Is the recent sales jump real?
    sustained_surge  -> >=30% above forecast, on >=5 of the last 7 days: trust recent sales
    single_day_spike -> high average but only 1-2 elevated days: probably an outlier
    ambiguous        -> 3-4 elevated days: keep forecast, flag it
    normal           -> keep forecast"""
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
    return {"status": status, "effective_daily": effective, "forecast_daily": forecast,
            "avg_last_7": round(avg7, 1), "ratio_vs_forecast": round(ratio, 2),
            "elevated_days_of_7": elevated, "peak_day": max(last7)}


def target_position(daily, lead_days, safety):
    """Stock (on hand + incoming) we want when placing an order today."""
    return math.ceil(daily * (lead_days + policy.review_period_days) + safety)


def max_cover(target):
    return math.floor(policy.max_cover_factor * target)
