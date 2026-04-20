"""WeasyPrint PDF renderer for conflict reports."""

import logging
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger(__name__)


def render_report_pdf(report, snapshots: list, warnings: list) -> bytes:
    """
    Render a conflict report to PDF bytes.

    snapshots: list of (Region, snap_data_dict) tuples
    warnings: aggregated list of data-quality warning strings
    """
    context = {
        "report": report,
        "snapshots": snapshots,
        "warnings": warnings,
        "has_warnings": bool(warnings),
        "feedback_url": (
            f"{getattr(settings, 'CONFLICT_REPORT_FRONTEND_URL', 'http://localhost:5173')}"
            f"/conflict-reports/feedback/{report.feedback_token}"
        ),
        "disclaimer": (
            "AgriSight Risk Score (preliminary) — This classification is an automated proxy "
            "based on ACLED, UNHCR, CHIRPS, and Sentinel-2 data. It is NOT an official IPC "
            "classification. Use alongside field assessments and professional judgment."
        ),
    }
    html_content = render_to_string("conflict_reports/report.html", context)

    try:
        from weasyprint import HTML
        return HTML(string=html_content).write_pdf()
    except ImportError:
        logger.error("WeasyPrint not installed — PDF generation unavailable")
        raise RuntimeError("WeasyPrint not installed. Add 'weasyprint' to requirements.txt.")
