"""
Tests for the conflict_reports app.
Covers: CompositeScoreTests, ConflictReportViewTests, FeedbackTests.
"""

import uuid
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ConflictReport, ReportFeedback
from .score import (
    compute_ndvi_score, compute_conflict_score, compute_displacement_score,
    compute_rainfall_score, compute_composite, score_to_ipc_phase,
)

User = get_user_model()


class CompositeScoreTests(TestCase):
    """Unit tests for the composite score and IPC phase mapping."""

    # --- ndvi_score ---
    def test_ndvi_score_positive_anomaly_low_risk(self):
        self.assertAlmostEqual(compute_ndvi_score(50.0), 0.0)

    def test_ndvi_score_zero_anomaly_mid_risk(self):
        self.assertAlmostEqual(compute_ndvi_score(0.0), 50.0)

    def test_ndvi_score_negative_anomaly_high_risk(self):
        self.assertAlmostEqual(compute_ndvi_score(-50.0), 100.0)

    def test_ndvi_score_none_returns_none(self):
        self.assertIsNone(compute_ndvi_score(None))

    # --- conflict_score ---
    def test_conflict_score_zero(self):
        self.assertAlmostEqual(compute_conflict_score(0), 0.0)

    def test_conflict_score_max(self):
        self.assertAlmostEqual(compute_conflict_score(200), 100.0)

    def test_conflict_score_overflow_clamps(self):
        self.assertAlmostEqual(compute_conflict_score(500), 100.0)

    def test_conflict_score_none_returns_none(self):
        self.assertIsNone(compute_conflict_score(None))

    # --- composite ---
    def test_all_present_weighted_correctly(self):
        score = compute_composite(50.0, 50.0, 50.0, 50.0)
        self.assertAlmostEqual(score, 50.0)

    def test_all_null_returns_none(self):
        self.assertIsNone(compute_composite(None, None, None, None))

    def test_partial_null_computes_from_available(self):
        # Only conflict (35% weight) = 100 → adjusted to 100
        score = compute_composite(None, 100.0, None, None)
        self.assertAlmostEqual(score, 100.0)

    def test_partial_null_two_signals(self):
        # ndvi=100 (30%), conflict=0 (35%) → weighted sum = 30/65 * 100 ≈ 46.15
        score = compute_composite(100.0, 0.0, None, None)
        expected = (0.30 * 100.0 + 0.35 * 0.0) / (0.30 + 0.35)
        self.assertAlmostEqual(score, round(expected, 2))

    # --- IPC phase boundaries ---
    def test_phase_boundary_0(self):
        self.assertIn("Phase 1", score_to_ipc_phase(0))

    def test_phase_boundary_20(self):
        self.assertIn("Phase 1", score_to_ipc_phase(20))

    def test_phase_boundary_21(self):
        self.assertIn("Phase 2", score_to_ipc_phase(21))

    def test_phase_boundary_40(self):
        self.assertIn("Phase 2", score_to_ipc_phase(40))

    def test_phase_boundary_41(self):
        self.assertIn("Phase 3", score_to_ipc_phase(41))

    def test_phase_boundary_60(self):
        self.assertIn("Phase 3", score_to_ipc_phase(60))

    def test_phase_boundary_61(self):
        self.assertIn("Phase 4", score_to_ipc_phase(61))

    def test_phase_boundary_80(self):
        self.assertIn("Phase 4", score_to_ipc_phase(80))

    def test_phase_boundary_81(self):
        self.assertIn("Phase 5", score_to_ipc_phase(81))

    def test_phase_boundary_100(self):
        self.assertIn("Phase 5", score_to_ipc_phase(100))

    def test_none_score_returns_data_unavailable(self):
        self.assertEqual(score_to_ipc_phase(None), "data_unavailable")


class ConflictReportViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="analyst@test.com", password="testpass123"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com", password="testpass123"
        )
        self.client.force_authenticate(user=self.user)

    def _make_report(self, user=None, **kwargs):
        defaults = dict(
            user=user or self.user,
            district_ids=[1, 2],
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=1),
        )
        defaults.update(kwargs)
        return ConflictReport.objects.create(**defaults)

    # --- generate ---
    def test_generate_valid_returns_202(self):
        with patch("apps.conflict_reports.views.generate_conflict_report") as mock_task:
            mock_task.delay.return_value = MagicMock(id="celery-id-123")
            resp = self.client.post("/api/v1/conflict-reports/generate/", {
                "district_ids": [1, 2],
                "start_date": str(date.today() - timedelta(days=30)),
                "end_date": str(date.today() - timedelta(days=1)),
            }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn("id", resp.data)

    def test_generate_unauthenticated_returns_403(self):
        self.client.logout()
        resp = self.client.post("/api/v1/conflict-reports/generate/", {
            "district_ids": [1],
            "start_date": str(date.today() - timedelta(days=10)),
            "end_date": str(date.today() - timedelta(days=1)),
        }, format="json")
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_generate_91_day_range_returns_400(self):
        resp = self.client.post("/api/v1/conflict-reports/generate/", {
            "district_ids": [1],
            "start_date": str(date.today() - timedelta(days=92)),
            "end_date": str(date.today() - timedelta(days=1)),
        }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_exactly_90_days_is_allowed(self):
        with patch("apps.conflict_reports.views.generate_conflict_report") as mock_task:
            mock_task.delay.return_value = MagicMock(id="celery-id-abc")
            resp = self.client.post("/api/v1/conflict-reports/generate/", {
                "district_ids": [1],
                "start_date": str(date.today() - timedelta(days=91)),
                "end_date": str(date.today() - timedelta(days=1)),
            }, format="json")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

    # --- status ---
    def test_status_own_report(self):
        report = self._make_report(status=ConflictReport.Status.PENDING)
        resp = self.client.get(f"/api/v1/conflict-reports/{report.id}/status/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["status"], "PENDING")

    def test_status_other_users_report_returns_404(self):
        report = self._make_report(user=self.other_user)
        resp = self.client.get(f"/api/v1/conflict-reports/{report.id}/status/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    # --- download ---
    def test_download_not_ready_returns_409(self):
        report = self._make_report(status=ConflictReport.Status.PROCESSING)
        resp = self.client.get(f"/api/v1/conflict-reports/{report.id}/download/")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_download_other_users_report_returns_404(self):
        report = self._make_report(user=self.other_user, status=ConflictReport.Status.COMPLETE)
        resp = self.client.get(f"/api/v1/conflict-reports/{report.id}/download/")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class FeedbackTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="analyst2@test.com", password="testpass")
        self.report = ConflictReport.objects.create(
            user=self.user,
            district_ids=[1],
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() - timedelta(days=1),
            status=ConflictReport.Status.COMPLETE,
        )

    def test_feedback_valid_token_no_auth_required(self):
        resp = self.client.post(
            f"/api/v1/conflict-reports/feedback/{self.report.feedback_token}/",
            {"accuracy_rating": 4, "missing_data": "Some ACLED gaps", "would_use_again": True},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(ReportFeedback.objects.filter(report=self.report).exists())

    def test_feedback_second_submission_is_idempotent(self):
        self.client.post(
            f"/api/v1/conflict-reports/feedback/{self.report.feedback_token}/",
            {"accuracy_rating": 3, "would_use_again": False},
            format="json",
        )
        self.client.post(
            f"/api/v1/conflict-reports/feedback/{self.report.feedback_token}/",
            {"accuracy_rating": 5, "would_use_again": True},
            format="json",
        )
        self.assertEqual(ReportFeedback.objects.filter(report=self.report).count(), 1)
        self.assertEqual(ReportFeedback.objects.get(report=self.report).accuracy_rating, 5)

    def test_wrong_feedback_token_returns_403(self):
        resp = self.client.post(
            f"/api/v1/conflict-reports/feedback/{uuid.uuid4()}/",
            {"accuracy_rating": 4},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_accuracy_rating_out_of_range_returns_400(self):
        resp = self.client.post(
            f"/api/v1/conflict-reports/feedback/{self.report.feedback_token}/",
            {"accuracy_rating": 6},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
