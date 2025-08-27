from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Sum
from datetime import datetime, timedelta
from .models import AgriculturalStressEvent, ConflictEvent
from .serializers import (
    AgriculturalStressEventSerializer, AgriculturalStressEventCreateSerializer,
    ConflictEventSerializer, ConflictEventCreateSerializer,
    StressEventSummarySerializer, ConflictEventSummarySerializer
)
from apps.geospatial.models import Region


class AgriculturalStressEventListCreateView(generics.ListCreateAPIView):
    """List all stress events or create a new one."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['region', 'stress_type', 'severity', 'is_verified']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AgriculturalStressEventCreateSerializer
        return AgriculturalStressEventSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return AgriculturalStressEvent.objects.all().select_related('region', 'crop_mapping__crop')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return AgriculturalStressEvent.objects.filter(
                region__in=accessible_regions
            ).select_related('region', 'crop_mapping__crop')
        else:
            return AgriculturalStressEvent.objects.none()


class AgriculturalStressEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a stress event."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AgriculturalStressEventCreateSerializer
        return AgriculturalStressEventSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return AgriculturalStressEvent.objects.all().select_related('region', 'crop_mapping__crop')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return AgriculturalStressEvent.objects.filter(
                region__in=accessible_regions
            ).select_related('region', 'crop_mapping__crop')
        else:
            return AgriculturalStressEvent.objects.none()


class ConflictEventListCreateView(generics.ListCreateAPIView):
    """List all conflict events or create a new one."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['region', 'event_type', 'intensity']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConflictEventCreateSerializer
        return ConflictEventSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return ConflictEvent.objects.all().select_related('region')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return ConflictEvent.objects.filter(region__in=accessible_regions).select_related('region')
        else:
            return ConflictEvent.objects.none()


class ConflictEventDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a conflict event."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ConflictEventCreateSerializer
        return ConflictEventSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return ConflictEvent.objects.all().select_related('region')
        elif user.organization:
            accessible_regions = Region.objects.filter(organizations=user.organization)
            return ConflictEvent.objects.filter(region__in=accessible_regions).select_related('region')
        else:
            return ConflictEvent.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stress_event_summary(request):
    """Get summary statistics for stress events."""
    user = request.user
    
    # Get accessible regions
    if user.user_type == 'admin':
        accessible_regions = Region.objects.all()
    elif user.organization:
        accessible_regions = Region.objects.filter(organizations=user.organization)
    else:
        accessible_regions = Region.objects.none()
    
    # Filter events by accessible regions
    events = AgriculturalStressEvent.objects.filter(region__in=accessible_regions)
    
    # Get date range from query parameters
    days = int(request.GET.get('days', 30))
    start_date = datetime.now().date() - timedelta(days=days)
    recent_events = events.filter(detection_date__gte=start_date)
    
    # Calculate statistics
    total_events = events.count()
    events_by_type = dict(events.values('stress_type').annotate(count=Count('id')).values_list('stress_type', 'count'))
    events_by_severity = dict(events.values('severity').annotate(count=Count('id')).values_list('severity', 'count'))
    total_affected_area = events.aggregate(total=Sum('affected_area_hectares'))['total'] or 0
    
    # Get recent events
    recent_events_data = AgriculturalStressEventSerializer(
        recent_events.order_by('-detection_date')[:10],
        many=True
    ).data
    
    summary_data = {
        'total_events': total_events,
        'events_by_type': events_by_type,
        'events_by_severity': events_by_severity,
        'total_affected_area': total_affected_area,
        'recent_events': recent_events_data
    }
    
    serializer = StressEventSummarySerializer(summary_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def conflict_event_summary(request):
    """Get summary statistics for conflict events."""
    user = request.user
    
    # Get accessible regions
    if user.user_type == 'admin':
        accessible_regions = Region.objects.all()
    elif user.organization:
        accessible_regions = Region.objects.filter(organizations=user.organization)
    else:
        accessible_regions = Region.objects.none()
    
    # Filter events by accessible regions
    events = ConflictEvent.objects.filter(region__in=accessible_regions)
    
    # Get date range from query parameters
    days = int(request.GET.get('days', 30))
    start_date = datetime.now().date() - timedelta(days=days)
    recent_events = events.filter(event_date__gte=start_date)
    
    # Calculate statistics
    total_events = events.count()
    events_by_type = dict(events.values('event_type').annotate(count=Count('id')).values_list('event_type', 'count'))
    events_by_intensity = dict(events.values('intensity').annotate(count=Count('id')).values_list('intensity', 'count'))
    
    # Get recent events
    recent_events_data = ConflictEventSerializer(
        recent_events.order_by('-event_date')[:10],
        many=True
    ).data
    
    summary_data = {
        'total_events': total_events,
        'events_by_type': events_by_type,
        'events_by_intensity': events_by_intensity,
        'recent_events': recent_events_data
    }
    
    serializer = ConflictEventSummarySerializer(summary_data)
    return Response(serializer.data)

