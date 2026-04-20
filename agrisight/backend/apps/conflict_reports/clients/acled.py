"""ACLED API client for conflict event data."""

import logging
import requests
from datetime import date
from django.conf import settings

logger = logging.getLogger(__name__)

ACLED_BASE_URL = "https://api.acleddata.com/acled/read"
ACLED_PAGE_SIZE = 500   # max events per page (ACLED default max)
ACLED_MAX_EVENTS = 50_000  # hard cap to prevent runaway pagination

DRC_TARGET_REGIONS = ["North Kivu", "Sud-Kivu", "Ituri"]


def fetch_conflict_events(district_name: str, aliases: list, start_date: date, end_date: date) -> dict:
    """
    Fetch ACLED conflict events for a district, paginating until all results are collected.

    Returns dict with keys: event_count, fatalities, events_detail, warnings.
    """
    api_key = getattr(settings, 'ACLED_API_KEY', '')
    email = getattr(settings, 'ACLED_EMAIL', '')

    if not api_key or not email:
        logger.warning("ACLED credentials not configured")
        return {"event_count": None, "fatalities": None, "events_detail": [], "warnings": ["ACLED credentials not configured"]}

    all_names = [district_name] + (aliases or [])
    base_params = {
        "key": api_key,
        "email": email,
        "event_date": f"{start_date.isoformat()}|{end_date.isoformat()}",
        "event_date_where": "BETWEEN",
        "country": "Democratic Republic of Congo",
        "admin2": "|".join(all_names),
        "fields": "event_date|event_type|admin2|fatalities|latitude|longitude",
        "limit": ACLED_PAGE_SIZE,
        "format": "json",
    }

    all_events = []
    capped = False
    page = 1

    try:
        while True:
            params = {**base_params, "page": page}
            response = requests.get(ACLED_BASE_URL, params=params, timeout=20)
            response.raise_for_status()
            page_events = response.json().get("data", [])
            all_events.extend(page_events)

            if len(page_events) < ACLED_PAGE_SIZE:
                break

            if len(all_events) >= ACLED_MAX_EVENTS:
                capped = True
                break

            page += 1

        warnings = []
        if capped:
            warnings.append(
                f"ACLED: event count capped at {ACLED_MAX_EVENTS} — actual count may be higher"
            )

        return {
            "event_count": len(all_events),
            "fatalities": sum(int(e.get("fatalities", 0) or 0) for e in all_events),
            "events_detail": all_events[:10],
            "warnings": warnings,
        }

    except requests.exceptions.Timeout:
        logger.warning("ACLED API timed out for district %s (page %d)", district_name, page)
        return {
            "event_count": None, "fatalities": None, "events_detail": [],
            "warnings": ["ACLED data unavailable for this period — conflict score estimated from last available data"],
        }
    except Exception as exc:
        logger.error("ACLED API error for %s: %s", district_name, exc)
        return {
            "event_count": None, "fatalities": None, "events_detail": [],
            "warnings": [f"ACLED data unavailable: {type(exc).__name__}"],
        }
