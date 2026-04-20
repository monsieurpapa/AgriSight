from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.GenerateReportView.as_view(), name='conflict-report-generate'),
    path('', views.ReportListView.as_view(), name='conflict-report-list'),
    path('<uuid:report_id>/', views.ReportDetailView.as_view(), name='conflict-report-detail'),
    path('<uuid:report_id>/status/', views.ReportStatusView.as_view(), name='conflict-report-status'),
    path('<uuid:report_id>/download/', views.ReportDownloadView.as_view(), name='conflict-report-download'),
    path('feedback/<uuid:feedback_token>/', views.FeedbackView.as_view(), name='conflict-report-feedback'),
]
