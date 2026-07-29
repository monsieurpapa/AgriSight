from datetime import date, timedelta
from rest_framework import serializers
from .models import ConflictReport, ReportDataSnapshot, ReportFeedback

MAX_DATE_RANGE_DAYS = 90


class GenerateReportSerializer(serializers.Serializer):
    district_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    recipient_email = serializers.EmailField(required=False, allow_blank=True, default="")

    def validate(self, data):
        start = data["start_date"]
        end = data["end_date"]
        if end <= start:
            raise serializers.ValidationError("end_date must be after start_date.")
        if (end - start).days > MAX_DATE_RANGE_DAYS:
            raise serializers.ValidationError(f"Date range cannot exceed {MAX_DATE_RANGE_DAYS} days.")
        if end > date.today():
            raise serializers.ValidationError("end_date cannot be in the future.")
        return data


class ReportDataSnapshotSerializer(serializers.ModelSerializer):
    district_name = serializers.CharField(source="region.name", read_only=True)
    province = serializers.CharField(source="region.province", read_only=True)

    class Meta:
        model = ReportDataSnapshot
        fields = [
            "district_name", "province",
            "ndvi_current", "ndvi_baseline_mean", "ndvi_anomaly",
            "conflict_event_count", "conflict_density_score",
            "idp_count", "displacement_score",
            "rainfall_mm", "rainfall_deviation_pct", "rainfall_score",
            "health_confirmed_cases", "health_suspected_cases", "health_deaths",
            "health_alert_score", "health_data_as_of",
            "composite_score", "ipc_phase_proxy",
            "data_warnings",
        ]


class ConflictReportSerializer(serializers.ModelSerializer):
    snapshots = ReportDataSnapshotSerializer(many=True, read_only=True)

    class Meta:
        model = ConflictReport
        fields = [
            "id", "status", "start_date", "end_date", "district_ids",
            "recipient_email", "email_status", "error_message",
            "created_at", "updated_at", "snapshots",
        ]
        read_only_fields = fields


class ConflictReportStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConflictReport
        fields = ["id", "status", "email_status", "error_message", "created_at", "updated_at"]
        read_only_fields = fields


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportFeedback
        fields = ["accuracy_rating", "missing_data", "would_use_again"]

    def validate_accuracy_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("accuracy_rating must be between 1 and 5.")
        return value
