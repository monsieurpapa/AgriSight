"""Composite risk score and IPC phase proxy calculator."""

from typing import Optional

# Weights (sum to 1.0)
WEIGHTS = {
    "ndvi_anomaly": 0.30,
    "conflict_density": 0.35,
    "displacement_flow": 0.25,
    "rainfall_deviation": 0.10,
}

# IPC Phase proxy mapping
IPC_PHASES = [
    (0, 20, "Phase 1 — Minimal"),
    (21, 40, "Phase 2 — Stressed"),
    (41, 60, "Phase 3 — Crisis"),
    (61, 80, "Phase 4 — Emergency"),
    (81, 100, "Phase 5 — Catastrophe/Famine"),
]

# Normalisation reference values for eastern DRC
# Conflict: 0 events = 0 score, 200+ events = 100 score
MAX_CONFLICT_EVENTS = 200
# Displacement: 0 IDPs = 0 score, 500,000+ IDPs = 100 score
MAX_IDP = 500_000
# NDVI anomaly: ±50% deviation maps to 0-100 risk
NDVI_ANOMALY_MAX_NEGATIVE = -50.0  # -50% = max vegetation stress
# Rainfall: -60% deviation (drought) = 100 risk; +60% (flood) = also high risk
RAINFALL_DEV_MAX = 60.0
# Health alert: 0 confirmed cases = 0 score, 500+ confirmed cases = 100 score (informational proxy only)
MAX_HEALTH_CASES = 500


def compute_ndvi_score(ndvi_anomaly_pct: Optional[float]) -> Optional[float]:
    """Convert NDVI % anomaly to 0-100 risk score. Negative anomaly = higher risk."""
    if ndvi_anomaly_pct is None:
        return None
    # Clamp and invert: -50% anomaly → 100 risk, 0% → 50 risk, +50% → 0 risk
    clamped = max(-50.0, min(50.0, ndvi_anomaly_pct))
    return max(0.0, min(100.0, 50.0 - clamped))


def compute_conflict_score(event_count: Optional[int]) -> Optional[float]:
    """Normalise conflict event count to 0-100."""
    if event_count is None:
        return None
    return min(100.0, (event_count / MAX_CONFLICT_EVENTS) * 100.0)


def compute_displacement_score(idp_count: Optional[int]) -> Optional[float]:
    """Normalise IDP count to 0-100."""
    if idp_count is None:
        return None
    return min(100.0, (idp_count / MAX_IDP) * 100.0)


def compute_rainfall_score(deviation_pct: Optional[float]) -> Optional[float]:
    """Normalise rainfall deviation to 0-100. Both drought and flood increase risk."""
    if deviation_pct is None:
        return None
    abs_dev = abs(deviation_pct)
    return min(100.0, (abs_dev / RAINFALL_DEV_MAX) * 100.0)


def compute_health_alert_score(confirmed_cases: Optional[float]) -> Optional[float]:
    """
    Normalise confirmed case count to 0-100.

    Informational only — deliberately excluded from WEIGHTS/compute_composite so it does
    not alter the existing IPC phase methodology. Surfaced in reports as a separate signal.
    """
    if confirmed_cases is None:
        return None
    return min(100.0, (confirmed_cases / MAX_HEALTH_CASES) * 100.0)


def compute_composite(
    ndvi_score: Optional[float],
    conflict_score: Optional[float],
    displacement_score: Optional[float],
    rainfall_score: Optional[float],
) -> Optional[float]:
    """
    Weighted composite 0-100.

    If ALL four signals are None, return None (data_unavailable, never Phase 1).
    If some are None, compute from available signals with adjusted weights.
    """
    scores = {
        "ndvi_anomaly": ndvi_score,
        "conflict_density": conflict_score,
        "displacement_flow": displacement_score,
        "rainfall_deviation": rainfall_score,
    }

    available = {k: v for k, v in scores.items() if v is not None}
    if not available:
        return None

    total_weight = sum(WEIGHTS[k] for k in available)
    weighted_sum = sum(WEIGHTS[k] * v for k, v in available.items())
    return round(weighted_sum / total_weight, 2)


def score_to_ipc_phase(composite: Optional[float]) -> str:
    if composite is None:
        return "data_unavailable"
    for low, high, label in IPC_PHASES:
        if low <= composite <= high:
            return label
    return "Phase 5 — Catastrophe/Famine"
