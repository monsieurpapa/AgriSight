"""CHIRPS rainfall anomaly client — direct GeoTIFF download from Climate Hazards Group (UCSB)."""

import gzip
import io
import logging
import os
import tempfile
from datetime import date

import requests

logger = logging.getLogger(__name__)

CHIRPS_BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs"

# 30-year monthly climatology for eastern DRC (rough mid-range across North Kivu / Sud-Kivu / Ituri).
# Used when the RainfallBaseline cache is empty. Far better than a single annual constant.
# Source: CHIRPS v2.0 long-term means, approximate values for 25-30°E / 0-5°S.
DRC_EASTERN_MONTHLY_MM = {
    1: 135.0, 2: 110.0, 3: 130.0, 4: 145.0, 5: 105.0, 6: 40.0,
    7: 20.0, 8: 25.0, 9: 80.0, 10: 120.0, 11: 140.0, 12: 135.0,
}


def fetch_rainfall_anomaly(geometry_geojson: str, start_date: date, end_date: date, district=None) -> dict:
    """
    Fetch CHIRPS monthly rainfall for a district and compute deviation from baseline.

    geometry_geojson: GeoJSON string (Polygon or MultiPolygon) of the district boundary.
    district: Region ORM object for cache lookup (optional, improves baseline quality).
    Returns dict with keys: rainfall_mm, deviation_pct, warnings.
    """
    try:
        from rasterstats import zonal_stats
    except ImportError:
        logger.error("rasterstats not installed")
        return {"rainfall_mm": None, "deviation_pct": None, "warnings": ["CHIRPS: rasterstats not installed"]}

    warnings = []
    centre = start_date + (end_date - start_date) / 2
    year, month = centre.year, centre.month

    rainfall_mm = _download_and_zonal_stats(geometry_geojson, year, month, warnings)
    if rainfall_mm is None:
        return {"rainfall_mm": None, "deviation_pct": None, "warnings": warnings}

    baseline_mm = _get_baseline(district, month, warnings)
    if baseline_mm is None or baseline_mm == 0:
        return {"rainfall_mm": rainfall_mm, "deviation_pct": None, "warnings": warnings}

    deviation_pct = ((rainfall_mm - baseline_mm) / baseline_mm) * 100.0
    return {"rainfall_mm": rainfall_mm, "deviation_pct": deviation_pct, "warnings": warnings}


def _download_and_zonal_stats(geometry_geojson: str, year: int, month: int, warnings: list):
    """Download monthly CHIRPS GeoTIFF and return the zonal mean (mm) for the district polygon."""
    from rasterstats import zonal_stats

    filename = f"chirps-v2.0.{year}.{month:02d}.tif.gz"
    url = f"{CHIRPS_BASE_URL}/{filename}"

    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        warnings.append("CHIRPS: download timed out")
        return None
    except Exception as exc:
        warnings.append(f"CHIRPS: download failed ({type(exc).__name__})")
        return None

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
            tmp_path = tmp.name
            with gzip.GzipFile(fileobj=io.BytesIO(resp.content)) as gz:
                tmp.write(gz.read())

        stats = zonal_stats(geometry_geojson, tmp_path, stats=["mean"], geojson_out=False)
        mean_val = stats[0].get("mean") if stats else None
        if mean_val is None:
            warnings.append("CHIRPS: no valid pixels in district geometry")
        return float(mean_val) if mean_val is not None else None

    except Exception as exc:
        warnings.append(f"CHIRPS: processing failed ({type(exc).__name__})")
        return None
    finally:
        if tmp_path:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass


def _get_baseline(district, month: int, warnings: list):
    """
    Return the monthly rainfall baseline (mm) for this district.
    Tries the RainfallBaseline DB cache first; falls back to the regional monthly table.
    """
    if district is not None:
        try:
            from apps.conflict_reports.models import RainfallBaseline
            return RainfallBaseline.objects.get(region=district, month=month).mean_mm
        except Exception:
            pass

    baseline = DRC_EASTERN_MONTHLY_MM.get(month)
    if baseline is None:
        warnings.append("CHIRPS: no climatology baseline for this month")
    return baseline
