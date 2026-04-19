import logging
from django.http import FileResponse, Http404
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConflictReport, ReportFeedback
from .serializers import (
    GenerateReportSerializer,
    ConflictReportSerializer,
    ConflictReportStatusSerializer,
    FeedbackSerializer,
)
from .tasks import generate_conflict_report

logger = logging.getLogger(__name__)


class ReportAccessTokenPermission:
    """Simple shared-token check for Approach A (single-user pilot)."""

    def has_permission(self, request, view):
        expected = getattr(settings, 'REPORT_ACCESS_TOKEN', '')
        if not expected:
            return False
        token = request.headers.get('X-Report-Token') or request.query_params.get('token')
        return token == expected


class GenerateReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        report = ConflictReport.objects.create(
            user=request.user,
            district_ids=data["district_ids"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            recipient_email=data.get("recipient_email", ""),
            email_status=(
                ConflictReport.EmailStatus.PENDING
                if data.get("recipient_email")
                else ConflictReport.EmailStatus.NOT_REQUESTED
            ),
        )

        task = generate_conflict_report.delay(str(report.id))
        report.celery_task_id = task.id
        report.save(update_fields=["celery_task_id"])

        return Response(
            {"id": str(report.id), "status": report.status},
            status=status.HTTP_202_ACCEPTED,
        )


class ReportStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        report = self._get_own_report(request.user, report_id)
        serializer = ConflictReportStatusSerializer(report)
        return Response(serializer.data)

    def _get_own_report(self, user, report_id):
        try:
            return ConflictReport.objects.get(id=report_id, user=user)
        except ConflictReport.DoesNotExist:
            raise Http404


class ReportDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = ConflictReport.objects.get(id=report_id, user=request.user)
        except ConflictReport.DoesNotExist:
            raise Http404

        if report.status != ConflictReport.Status.COMPLETE or not report.pdf_file:
            return Response(
                {"detail": "Report is not ready yet.", "status": report.status},
                status=status.HTTP_409_CONFLICT,
            )

        return FileResponse(
            report.pdf_file.open("rb"),
            as_attachment=True,
            filename=report.pdf_file.name.split("/")[-1],
            content_type="application/pdf",
        )


class ReportDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, report_id):
        try:
            report = ConflictReport.objects.prefetch_related("snapshots__region").get(
                id=report_id, user=request.user
            )
        except ConflictReport.DoesNotExist:
            raise Http404
        return Response(ConflictReportSerializer(report).data)


class ReportListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reports = ConflictReport.objects.filter(user=request.user).order_by("-created_at")[:20]
        return Response(ConflictReportStatusSerializer(reports, many=True).data)


class FeedbackView(APIView):
    """Unauthenticated feedback endpoint. Token validated via feedback_token UUID."""

    permission_classes = [AllowAny]

    def post(self, request, feedback_token):
        try:
            report = ConflictReport.objects.get(feedback_token=feedback_token)
        except ConflictReport.DoesNotExist:
            # Return 403 (not 404) to avoid confirming report existence
            return Response({"detail": "Invalid token."}, status=status.HTTP_403_FORBIDDEN)

        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ReportFeedback.objects.update_or_create(
            report=report,
            defaults=serializer.validated_data,
        )

        return Response({"detail": "Thank you for your feedback."}, status=status.HTTP_200_OK)
