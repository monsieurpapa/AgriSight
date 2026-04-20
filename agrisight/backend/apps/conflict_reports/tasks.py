"""Celery tasks for conflict report generation."""

import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from datetime import date, timedelta

from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings

from apps.geospatial.models import Region
from .models import ConflictReport, NDVIBaseline, RainfallBaseline, ReportDataSnapshot
from .clients.acled import fetch_conflict_events
from .clients.unhcr import fetch_displacement_data
from .clients.chirps import fetch_rainfall_anomaly
from .score import (
    compute_ndvi_score, compute_conflict_score,
    compute_displacement_score, compute_rainfall_score,
    compute_composite, score_to_ipc_phase,
)
from .pdf import render_report_pdf

logger = logging.getLogger(__name__)

TASK_TIMEOUT_SECONDS = 30


@shared_task(bind=True, max_retries=0, time_limit=TASK_TIMEOUT_SECONDS + 5)
def generate_conflict_report(self, report_id: str):
    """
    Generate a conflict-aware food security report PDF.

    Wall-clock budget: 30s total. Each external API call gets fut.result(timeout=25).
    If an API fails, we include partial data with a visible warning in the PDF.
    """
    from .models import ConflictReport

    try:
        report = ConflictReport.objects.get(id=report_id)
    except ConflictReport.DoesNotExist:
        logger.error("ConflictReport %s not found", report_id)
        return

    report.status = ConflictReport.Status.PROCESSING
    report.save(update_fields=["status"])

    districts = Region.objects.filter(pk__in=report.district_ids)
    start = report.start_date
    end = report.end_date

    snapshots = []
    all_warnings = []

    for district in districts:
        snap_data = _fetch_district_data(district, start, end)
        all_warnings.extend(snap_data.get("warnings", []))

        ndvi_score = compute_ndvi_score(snap_data.get("ndvi_anomaly"))
        conflict_score = compute_conflict_score(snap_data.get("conflict_event_count"))
        displacement_score = compute_displacement_score(snap_data.get("idp_count"))
        rainfall_score = compute_rainfall_score(snap_data.get("rainfall_deviation_pct"))

        composite = compute_composite(ndvi_score, conflict_score, displacement_score, rainfall_score)
        ipc_phase = score_to_ipc_phase(composite)

        snap_data["ndvi_score"] = ndvi_score
        snap_data["conflict_density_score"] = conflict_score
        snap_data["displacement_score"] = displacement_score
        snap_data["rainfall_score"] = rainfall_score
        snap_data["composite_score"] = composite
        snap_data["ipc_phase_proxy"] = ipc_phase

        snapshots.append((district, snap_data))

    # Persist snapshots
    for district, snap_data in snapshots:
        ReportDataSnapshot.objects.update_or_create(
            report=report,
            region=district,
            defaults={
                "ndvi_current": snap_data.get("ndvi_current"),
                "ndvi_baseline_mean": snap_data.get("ndvi_baseline_mean"),
                "ndvi_anomaly": snap_data.get("ndvi_anomaly"),
                "conflict_event_count": snap_data.get("conflict_event_count"),
                "conflict_density_score": snap_data.get("conflict_density_score"),
                "idp_count": snap_data.get("idp_count"),
                "displacement_score": snap_data.get("displacement_score"),
                "rainfall_mm": snap_data.get("rainfall_mm"),
                "rainfall_deviation_pct": snap_data.get("rainfall_deviation_pct"),
                "rainfall_score": snap_data.get("rainfall_score"),
                "composite_score": snap_data.get("composite_score"),
                "ipc_phase_proxy": snap_data.get("ipc_phase_proxy", ""),
                "data_warnings": snap_data.get("warnings", []),
                "signals_detail": snap_data.get("signals_detail", {}),
            },
        )

    # Generate PDF
    try:
        pdf_bytes = render_report_pdf(report, snapshots, all_warnings)
    except Exception as exc:
        logger.error("PDF generation failed for report %s: %s", report_id, exc)
        report.status = ConflictReport.Status.FAILED
        report.error_message = f"PDF generation error: {exc}"
        report.save(update_fields=["status", "error_message"])
        return

    # Save PDF file
    import io
    from django.core.files.base import ContentFile
    filename = f"conflict_report_{report_id[:8]}_{start}_{end}.pdf"
    report.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
    report.status = ConflictReport.Status.COMPLETE
    report.save(update_fields=["status", "pdf_file"])

    # Send email if requested
    if report.recipient_email:
        _send_report_email(report, pdf_bytes, filename)


def _fetch_district_data(district: Region, start: date, end: date) -> dict:
    """
    Fetch all 4 signals for one district concurrently with a 25s wall-clock timeout.
    Returns merged dict with all signal values and a combined warnings list.
    """
    bbox = list(district.geometry.extent)  # [min_lon, min_lat, max_lon, max_lat]

    # Get NDVI baseline (cached; fallback to inline fetch if not available)
    baseline_mean, baseline_std = _get_ndvi_baseline(district, bbox)

    def fetch_ndvi():
        return _fetch_ndvi_current(district, bbox, start, end)

    def fetch_acled():
        return fetch_conflict_events(district.name, district.acled_name_aliases, start, end)

    def fetch_unhcr():
        return fetch_displacement_data(district.name, district.province, start, end)

    def fetch_chirps():
        return fetch_rainfall_anomaly(district.geometry.geojson, start, end, district=district)

    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            "ndvi": executor.submit(fetch_ndvi),
            "acled": executor.submit(fetch_acled),
            "unhcr": executor.submit(fetch_unhcr),
            "chirps": executor.submit(fetch_chirps),
        }
        for key, fut in futures.items():
            try:
                results[key] = fut.result(timeout=25)
            except FuturesTimeout:
                logger.warning("Timeout fetching %s for district %s", key, district.name)
                results[key] = {"warnings": [f"{key.upper()} data unavailable — timeout"]}
            except Exception as exc:
                logger.error("Error fetching %s for %s: %s", key, district.name, exc)
                results[key] = {"warnings": [f"{key.upper()} data unavailable: {type(exc).__name__}"]}

    ndvi_result = results.get("ndvi", {})
    acled_result = results.get("acled", {})
    unhcr_result = results.get("unhcr", {})
    chirps_result = results.get("chirps", {})

    ndvi_current = ndvi_result.get("ndvi_current")
    ndvi_anomaly = None
    if ndvi_current is not None and baseline_mean is not None and baseline_mean != 0:
        ndvi_anomaly = ((ndvi_current - baseline_mean) / abs(baseline_mean)) * 100.0

    all_warnings = (
        ndvi_result.get("warnings", [])
        + acled_result.get("warnings", [])
        + unhcr_result.get("warnings", [])
        + chirps_result.get("warnings", [])
    )

    return {
        "ndvi_current": ndvi_current,
        "ndvi_baseline_mean": baseline_mean,
        "ndvi_anomaly": ndvi_anomaly,
        "conflict_event_count": acled_result.get("event_count"),
        "idp_count": unhcr_result.get("idp_count"),
        "rainfall_mm": chirps_result.get("rainfall_mm"),
        "rainfall_deviation_pct": chirps_result.get("deviation_pct"),
        "warnings": all_warnings,
        "signals_detail": {
            "acled_sample": acled_result.get("events_detail", []),
            "unhcr_province_total": unhcr_result.get("province_total"),
        },
    }


def _get_ndvi_baseline(district: Region, bbox: list) -> tuple:
    """Return (mean, std) from NDVIBaseline cache, or fetch inline and cache."""
    try:
        baseline = NDVIBaseline.objects.get(region=district)
        return baseline.mean_ndvi, baseline.std_ndvi
    except NDVIBaseline.DoesNotExist:
        pass

    # Inline fetch: compute 3-year baseline now
    try:
        mean, std = _compute_ndvi_baseline_inline(district, bbox)
        NDVIBaseline.objects.update_or_create(
            region=district,
            defaults={"mean_ndvi": mean, "std_ndvi": std, "baseline_years": 3},
        )
        return mean, std
    except Exception as exc:
        logger.warning("Could not compute NDVI baseline for %s: %s", district.name, exc)
        return None, None


def _compute_ndvi_baseline_inline(district: Region, bbox: list) -> tuple:
    """
    Compute 3-year NDVI baseline using Sentinel Hub Statistical API.
    For large districts (bbox area > ~10,000 km²), subdivide into 4 quadrants.
    """
    from apps.sentinel_hub.client import SentinelHubClient
    from datetime import datetime

    client = SentinelHubClient()
    evalscript = """
    //VERSION=3
    function setup() {
        return {input: [{bands: ["B04","B08"]}], output: {bands: 1, sampleType: "FLOAT32"}};
    }
    function evaluatePixel(s) {
        let denom = s.B08 + s.B04;
        return denom > 0 ? [(s.B08 - s.B04) / denom] : [0.0];
    }
    """

    today = date.today()
    baseline_end = date(today.year - 1, 12, 31)
    baseline_start = date(today.year - 4, 1, 1)
    time_range = (f"{baseline_start}T00:00:00Z", f"{baseline_end}T23:59:59Z")

    bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) * 12321  # rough km²
    bboxes = _subdivide_bbox(bbox) if bbox_area > 10000 else [bbox]

    all_means = []
    for sub_bbox in bboxes:
        try:
            result = client.statistical_request(sub_bbox, time_range, evalscript, timeout=20)
            data = result.get("data", [])
            for bucket in data:
                outputs = bucket.get("outputs", {})
                b0 = outputs.get("B0", outputs.get("default", {}))
                stats = b0.get("statistics", {}) if isinstance(b0, dict) else {}
                mean = stats.get("mean")
                if mean is not None:
                    all_means.append(float(mean))
        except Exception as exc:
            logger.warning("Statistical API failed for sub-bbox %s: %s", sub_bbox, exc)

    if not all_means:
        raise ValueError("No NDVI values returned from Statistical API")

    import statistics
    mean = statistics.mean(all_means)
    std = statistics.stdev(all_means) if len(all_means) > 1 else 0.05
    return mean, std


def _subdivide_bbox(bbox: list) -> list:
    """Split bbox into 4 equal quadrants."""
    min_lon, min_lat, max_lon, max_lat = bbox
    mid_lon = (min_lon + max_lon) / 2
    mid_lat = (min_lat + max_lat) / 2
    return [
        [min_lon, min_lat, mid_lon, mid_lat],
        [mid_lon, min_lat, max_lon, mid_lat],
        [min_lon, mid_lat, mid_lon, max_lat],
        [mid_lon, mid_lat, max_lon, max_lat],
    ]


def _fetch_ndvi_current(district: Region, bbox: list, start: date, end: date) -> dict:
    """Fetch current period NDVI mean via Sentinel Hub Statistical API."""
    from apps.sentinel_hub.client import SentinelHubClient

    client = SentinelHubClient()
    evalscript = """
    //VERSION=3
    function setup() {
        return {input: [{bands: ["B04","B08"]}], output: {bands: 1, sampleType: "FLOAT32"}};
    }
    function evaluatePixel(s) {
        let denom = s.B08 + s.B04;
        return denom > 0 ? [(s.B08 - s.B04) / denom] : [0.0];
    }
    """
    time_range = (f"{start}T00:00:00Z", f"{end}T23:59:59Z")

    try:
        result = client.statistical_request(bbox, time_range, evalscript, timeout=20)
        data = result.get("data", [])
        means = []
        for bucket in data:
            outputs = bucket.get("outputs", {})
            b0 = outputs.get("B0", outputs.get("default", {}))
            stats = b0.get("statistics", {}) if isinstance(b0, dict) else {}
            mean = stats.get("mean")
            if mean is not None:
                means.append(float(mean))
        if not means:
            return {"ndvi_current": None, "warnings": ["Sentinel Hub: no NDVI data returned for period"]}
        import statistics
        return {"ndvi_current": statistics.mean(means), "warnings": []}
    except Exception as exc:
        logger.warning("Sentinel Hub NDVI fetch failed for %s: %s", district.name, exc)
        return {"ndvi_current": None, "warnings": [f"Sentinel Hub NDVI data unavailable: {type(exc).__name__}"]}


def _send_report_email(report: ConflictReport, pdf_bytes: bytes, filename: str):
    """Send report PDF via email. Updates email_status field."""
    feedback_url = (
        f"{getattr(settings, 'CONFLICT_REPORT_FRONTEND_URL', 'http://localhost:5173')}"
        f"/conflict-reports/feedback/{report.feedback_token}"
    )
    body = (
        f"Please find attached your AgriSight conflict-aware food security report.\n\n"
        f"Period: {report.start_date} to {report.end_date}\n\n"
        f"Help us improve: {feedback_url}\n\n"
        f"— AgriSight"
    )
    try:
        email = EmailMessage(
            subject="AgriSight Food Security Report",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[report.recipient_email],
        )
        email.attach(filename, pdf_bytes, "application/pdf")
        email.send(fail_silently=False)
        report.email_status = ConflictReport.EmailStatus.SENT
    except Exception as exc:
        logger.error("Email delivery failed for report %s: %s", report.id, exc)
        report.email_status = ConflictReport.EmailStatus.FAILED
        report.error_message = (report.error_message + f"\nEmail failed: {exc}").strip()
    report.save(update_fields=["email_status", "error_message"])


@shared_task
def precompute_ndvi_baselines():
    """Celery beat task: pre-cache NDVI baselines for all DRC target districts."""
    target_provinces = ["North Kivu", "Sud-Kivu", "Ituri"]
    districts = Region.objects.filter(province__in=target_provinces, country__icontains="Congo")
    for district in districts:
        try:
            bbox = list(district.geometry.extent)
            mean, std = _compute_ndvi_baseline_inline(district, bbox)
            NDVIBaseline.objects.update_or_create(
                region=district,
                defaults={"mean_ndvi": mean, "std_ndvi": std, "baseline_years": 3},
            )
            logger.info("NDVI baseline cached for %s (mean=%.3f)", district.name, mean)
        except Exception as exc:
            logger.warning("Baseline precompute failed for %s: %s", district.name, exc)


@shared_task
def precompute_rainfall_baselines():
    """
    Celery beat task: pre-cache per-district per-month CHIRPS rainfall baselines.

    Downloads CHIRPS monthly GeoTIFFs for the past 10 years and computes zonal stats
    per district per calendar month. Stores results in RainfallBaseline.
    """
    from datetime import date, timedelta
    import statistics as pystats
    from .clients.chirps import _download_and_zonal_stats

    target_provinces = ["North Kivu", "Sud-Kivu", "Ituri"]
    districts = Region.objects.filter(province__in=target_provinces, country__icontains="Congo")

    today = date.today()
    # Collect 10 years of monthly data per calendar month
    years = list(range(today.year - 10, today.year))

    for district in districts:
        geojson = district.geometry.geojson
        month_values: dict = {m: [] for m in range(1, 13)}

        for year in years:
            for month in range(1, 13):
                if date(year, month, 1) >= today.replace(day=1):
                    continue
                try:
                    warnings: list = []
                    val = _download_and_zonal_stats(geojson, year, month, warnings)
                    if val is not None:
                        month_values[month].append(val)
                except Exception as exc:
                    logger.debug("CHIRPS fetch failed for %s %d-%02d: %s", district.name, year, month, exc)

        for month, values in month_values.items():
            if not values:
                continue
            try:
                mean = pystats.mean(values)
                std = pystats.stdev(values) if len(values) > 1 else 0.0
                RainfallBaseline.objects.update_or_create(
                    region=district,
                    month=month,
                    defaults={"mean_mm": mean, "std_mm": std, "baseline_years": len(values)},
                )
            except Exception as exc:
                logger.warning("RainfallBaseline save failed for %s month %d: %s", district.name, month, exc)

        logger.info("Rainfall baselines cached for %s", district.name)
