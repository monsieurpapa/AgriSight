from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Report, Alert
from .serializers import (
    ReportSerializer, ReportCreateSerializer,
    AlertSerializer, AlertCreateSerializer, AlertUpdateSerializer
)
from apps.geospatial.models import Region


class ReportListCreateView(generics.ListCreateAPIView):
    """List all reports or create a new report."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_type', 'is_published', 'organization']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReportCreateSerializer
        return ReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Report.objects.all().select_related('organization').prefetch_related('regions')
        elif user.organization:
            return Report.objects.filter(organization=user.organization).select_related('organization').prefetch_related('regions')
        else:
            return Report.objects.none()


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a report."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReportCreateSerializer
        return ReportSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Report.objects.all().select_related('organization').prefetch_related('regions')
        elif user.organization:
            return Report.objects.filter(organization=user.organization).select_related('organization').prefetch_related('regions')
        else:
            return Report.objects.none()


class AlertListCreateView(generics.ListCreateAPIView):
    """List all alerts or create a new alert."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['alert_type', 'severity', 'is_read', 'organization']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AlertCreateSerializer
        return AlertSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Alert.objects.all().select_related('organization', 'read_by').prefetch_related('regions')
        elif user.organization:
            return Alert.objects.filter(organization=user.organization).select_related('organization', 'read_by').prefetch_related('regions')
        else:
            return Alert.objects.none()


class AlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an alert."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AlertUpdateSerializer
        return AlertSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return Alert.objects.all().select_related('organization', 'read_by').prefetch_related('regions')
        elif user.organization:
            return Alert.objects.filter(organization=user.organization).select_related('organization', 'read_by').prefetch_related('regions')
        else:
            return Alert.objects.none()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_alert_as_read(request, alert_id):
    """Mark an alert as read."""
    try:
        user = request.user
        
        # Get the alert
        if user.user_type == 'admin':
            alert = Alert.objects.get(id=alert_id)
        elif user.organization:
            alert = Alert.objects.get(id=alert_id, organization=user.organization)
        else:
            return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Mark as read
        alert.is_read = True
        alert.read_by = user
        alert.read_at = timezone.now()
        alert.save()
        
        serializer = AlertSerializer(alert)
        return Response(serializer.data)
        
    except Alert.DoesNotExist:
        return Response({'error': 'Alert not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_alerts_as_read(request):
    """Mark all alerts for the user's organization as read."""
    user = request.user
    
    if not user.organization:
        return Response({'error': 'User not associated with any organization'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update all unread alerts for the organization
    updated_count = Alert.objects.filter(
        organization=user.organization,
        is_read=False
    ).update(
        is_read=True,
        read_by=user,
        read_at=timezone.now()
    )
    
    return Response({'message': f'Marked {updated_count} alerts as read'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_alerts_count(request):
    """Get count of unread alerts for the user's organization."""
    user = request.user
    
    if user.user_type == 'admin':
        count = Alert.objects.filter(is_read=False).count()
    elif user.organization:
        count = Alert.objects.filter(organization=user.organization, is_read=False).count()
    else:
        count = 0
    
    return Response({'unread_count': count})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recent_alerts(request):
    """Get recent alerts for the user's organization."""
    user = request.user
    limit = int(request.GET.get('limit', 10))
    
    if user.user_type == 'admin':
        alerts = Alert.objects.all().select_related('organization', 'read_by').prefetch_related('regions')
    elif user.organization:
        alerts = Alert.objects.filter(organization=user.organization).select_related('organization', 'read_by').prefetch_related('regions')
    else:
        alerts = Alert.objects.none()
    
    recent_alerts = alerts.order_by('-created_at')[:limit]
    serializer = AlertSerializer(recent_alerts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_report(request, pk):
    """Download a report as PDF or other format."""
    user = request.user
    
    # Get the report with proper permissions
    if user.user_type == 'admin':
        report = get_object_or_404(Report, pk=pk)
    elif user.organization:
        report = get_object_or_404(Report, pk=pk, organization=user.organization)
    else:
        raise Http404("Report not found")
    
    # For now, return a simple text response
    # In a real implementation, this would generate and return a PDF
    content = f"""
    Report: {report.title}
    Type: {report.report_type}
    Created: {report.created_at}
    Organization: {report.organization.name if report.organization else 'N/A'}
    
    Summary: {report.summary or 'No summary available'}
    """
    
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="report_{report.id}.txt"'
    return response

