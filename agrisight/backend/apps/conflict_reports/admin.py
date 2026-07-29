from django.contrib import admin
from .models import ConflictReport, NDVIBaseline, ReportDataSnapshot, ReportFeedback


@admin.register(ConflictReport)
class ConflictReportAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "start_date", "end_date", "email_status", "created_at"]
    list_filter = ["status", "email_status"]
    readonly_fields = ["id", "feedback_token", "celery_task_id", "created_at", "updated_at"]
    search_fields = ["user__email"]


@admin.register(NDVIBaseline)
class NDVIBaselineAdmin(admin.ModelAdmin):
    list_display = ["region", "mean_ndvi", "std_ndvi", "baseline_years", "computed_at"]


@admin.register(ReportDataSnapshot)
class ReportDataSnapshotAdmin(admin.ModelAdmin):
    list_display = ["report", "region", "composite_score", "ipc_phase_proxy", "health_confirmed_cases", "health_deaths"]
    list_filter = ["ipc_phase_proxy"]


@admin.register(ReportFeedback)
class ReportFeedbackAdmin(admin.ModelAdmin):
    list_display = ["report", "accuracy_rating", "would_use_again", "submitted_at"]
