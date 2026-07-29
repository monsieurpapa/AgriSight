"""HDX (Humanitarian Data Exchange) health-alert client — CKAN datastore_search for DRC epidemiological sitreps."""

import logging
from datetime import date, datetime, timedelta

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

HDX_PAGE_SIZE = 1000
HDX_MAX_RECORDS = 10_000  # hard cap to prevent runaway pagination
HDX_CACHE_TTL = 3600  # seconds — avoids re-pulling the full dataset once per district in a multi-district report
HDX_LOOKBACK_DAYS = 180  # how far before start_date to look for the last known cumulative total


def fetch_health_alerts(district_name: str, district_code: str, start_date: date, end_date: date) -> dict:
    """
    Fetch epidemiological sitrep data (confirmed/suspected cases, deaths) for a district.

    Values in the source dataset are cumulative-to-date per location/measure/classification,
    so this takes the latest record within the report window (or up to HDX_LOOKBACK_DAYS
    before start_date, if none fall inside the window) rather than summing daily rows,
    which would double-count.

    Returns dict with keys: confirmed_cases, suspected_cases, deaths, as_of_date, warnings.
    """
    empty = {
        "confirmed_cases": None, "suspected_cases": None, "deaths": None,
        "as_of_date": None, "warnings": [],
    }

    resource_id = getattr(settings, "HDX_RESOURCE_ID", "")
    if not resource_id:
        return {**empty, "warnings": ["HDX: resource not configured"]}

    records = _fetch_all_records(resource_id)
    if records is None:
        return {**empty, "warnings": ["HDX health-alert data unavailable"]}

    matched = [r for r in records if _matches_district(r, district_name, district_code)]
    if not matched:
        return empty

    lookback_start = start_date - timedelta(days=HDX_LOOKBACK_DAYS)
    candidates = [r for r in matched if lookback_start <= _record_date(r) <= end_date]
    if not candidates:
        return {
            **empty,
            "warnings": [f"HDX: no sitrep data for {district_name} within {HDX_LOOKBACK_DAYS}d lookback"],
        }

    latest_by_group = {}
    for record in candidates:
        key = (record.get("location_code"), record.get("measure"), record.get("case_classification"))
        current = latest_by_group.get(key)
        if current is None or _record_date(record) > _record_date(current):
            latest_by_group[key] = record

    confirmed_cases = _sum_values(latest_by_group, "cases", "confirmed")
    suspected_cases = _sum_values(latest_by_group, "cases", "suspected")
    deaths = _sum_values(latest_by_group, "deaths", None)

    as_of = max((_record_date(r) for r in latest_by_group.values()), default=None)
    warnings = []
    if as_of is not None and as_of < start_date:
        warnings.append(f"HDX: latest sitrep data is from {as_of.isoformat()} — predates report window")

    return {
        "confirmed_cases": confirmed_cases,
        "suspected_cases": suspected_cases,
        "deaths": deaths,
        "as_of_date": as_of,
        "warnings": warnings,
    }


def _fetch_all_records(resource_id: str):
    """Paginate the full COD sitrep dataset for a resource, cached briefly to avoid refetching per district."""
    cache_key = f"hdx_records:{resource_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    api_token = getattr(settings, "HDX_API_TOKEN", "")
    base_url = getattr(settings, "HDX_BASE_URL", "https://data.humdata.org/api/3/action/datastore_search")
    headers = {"Content-Type": "application/json"}
    if api_token:
        headers["Authorization"] = api_token

    all_records = []
    offset = 0
    try:
        while True:
            response = requests.post(
                base_url,
                headers=headers,
                json={
                    "resource_id": resource_id,
                    "filters": {"location_country": "COD"},
                    "limit": HDX_PAGE_SIZE,
                    "offset": offset,
                },
                timeout=20,
            )
            response.raise_for_status()
            payload = response.json()
            if not payload.get("success"):
                logger.error("HDX API returned success=false: %s", payload.get("error"))
                return None

            page = payload.get("result", {}).get("records", [])
            all_records.extend(page)

            if len(page) < HDX_PAGE_SIZE or len(all_records) >= HDX_MAX_RECORDS:
                break
            offset += HDX_PAGE_SIZE

        cache.set(cache_key, all_records, HDX_CACHE_TTL)
        return all_records

    except requests.exceptions.Timeout:
        logger.warning("HDX API timed out (offset=%d)", offset)
        return None
    except Exception as exc:
        logger.error("HDX API error: %s", exc)
        return None


def _matches_district(record: dict, district_name: str, district_code: str) -> bool:
    """Match on admin2 pcode prefix (precise) or fall back to a district-name substring match."""
    loc_code = record.get("location_code") or ""
    if district_code and loc_code and loc_code.startswith(district_code):
        return True

    loc_name = f"{record.get('location_name') or ''} {record.get('location_name_source') or ''}"
    return bool(district_name) and district_name.lower() in loc_name.lower()


def _record_date(record: dict) -> date:
    raw = record.get("reference_date")
    if not raw:
        return date.min
    try:
        return datetime.fromisoformat(raw.replace("Z", "")).date()
    except (ValueError, TypeError):
        return date.min


def _sum_values(latest_by_group: dict, measure: str, classification: str | None):
    """Sum the latest cumulative value across matched locations for a given measure (+ optional classification)."""
    total = None
    for (_, rec_measure, rec_classification), record in latest_by_group.items():
        if rec_measure != measure:
            continue
        if classification is not None and rec_classification != classification:
            continue
        value = record.get("value")
        if value is None:
            continue
        total = (total or 0) + value
    return total
