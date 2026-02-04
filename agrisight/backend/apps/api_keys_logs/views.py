from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg
from datetime import datetime, timedelta
import secrets
import hashlib
from .models import APIKey, AnalyticsLog
from .serializers import (
    APIKeySerializer, APIKeyCreateSerializer,
    AnalyticsLogSerializer, UsageStatsSerializer
)


class APIKeyListCreateView(generics.ListCreateAPIView):
    """List all API keys or create a new API key."""
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'is_active']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return APIKeyCreateSerializer
        return APIKeySerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return APIKey.objects.all().select_related('organization')
        elif user.organization:
            return APIKey.objects.filter(organization=user.organization).select_related('organization')
        else:
            return APIKey.objects.none()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        organization = serializer.validated_data.get('organization')
        if user.user_type != 'admin':
            if not user.organization:
                return Response({'error': 'Organization is required.'}, status=status.HTTP_400_BAD_REQUEST)
            organization = user.organization
        if not organization:
            return Response({'error': 'Organization is required.'}, status=status.HTTP_400_BAD_REQUEST)

        api_key = secrets.token_urlsafe(32)
        key_prefix = api_key[:8]
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()

        instance = serializer.save(
            organization=organization,
            key_prefix=key_prefix,
            key_hash=key_hash
        )

        data = APIKeySerializer(instance).data
        data['full_api_key'] = api_key
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an API key."""
    
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return APIKey.objects.all().select_related('organization')
        elif user.organization:
            return APIKey.objects.filter(organization=user.organization).select_related('organization')
        else:
            return APIKey.objects.none()


class AnalyticsLogListView(generics.ListAPIView):
    """List analytics logs."""
    
    serializer_class = AnalyticsLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['organization', 'action_type', 'resource_type', 'status_code']
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'admin':
            return AnalyticsLog.objects.all().select_related('organization', 'user')
        elif user.organization:
            return AnalyticsLog.objects.filter(organization=user.organization).select_related('organization', 'user')
        else:
            return AnalyticsLog.objects.none()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def usage_statistics(request):
    """Get usage statistics for the organization."""
    user = request.user
    
    # Get date range from query parameters
    days = int(request.GET.get('days', 30))
    start_date = datetime.now() - timedelta(days=days)
    
    # Get accessible logs
    if user.user_type == 'admin':
        logs = AnalyticsLog.objects.filter(created_at__gte=start_date)
    elif user.organization:
        logs = AnalyticsLog.objects.filter(
            organization=user.organization,
            created_at__gte=start_date
        )
    else:
        logs = AnalyticsLog.objects.none()
    
    # Calculate statistics
    total_requests = logs.count()
    
    requests_by_action = dict(
        logs.values('action_type').annotate(count=Count('id')).values_list('action_type', 'count')
    )
    
    requests_by_resource = dict(
        logs.values('resource_type').annotate(count=Count('id')).values_list('resource_type', 'count')
    )
    
    avg_response_time = logs.filter(response_time_ms__isnull=False).aggregate(
        avg=Avg('response_time_ms')
    )['avg'] or 0
    
    error_requests = logs.filter(status_code__gte=400).count()
    error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
    
    top_users = list(
        logs.filter(user__isnull=False)
        .values('user__username')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
        .values_list('user__username', 'count')
    )
    
    stats_data = {
        'total_requests': total_requests,
        'requests_by_action': requests_by_action,
        'requests_by_resource': requests_by_resource,
        'avg_response_time': round(avg_response_time, 2),
        'error_rate': round(error_rate, 2),
        'top_users': top_users
    }
    
    serializer = UsageStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def regenerate_api_key(request, pk):
    """Regenerate an API key."""
    user = request.user
    
    try:
        # Get the API key
        if user.user_type == 'admin':
            api_key_obj = APIKey.objects.get(id=pk)
        elif user.organization:
            api_key_obj = APIKey.objects.get(id=pk, organization=user.organization)
        else:
            return Response({'error': 'API key not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate new API key
        new_api_key = secrets.token_urlsafe(32)
        new_key_prefix = new_api_key[:8]
        new_key_hash = hashlib.sha256(new_api_key.encode()).hexdigest()
        
        # Update the API key
        api_key_obj.key_prefix = new_key_prefix
        api_key_obj.key_hash = new_key_hash
        api_key_obj.save()
        
        return Response({
            'message': 'API key regenerated successfully',
            'new_api_key': new_api_key,  # Only shown once
            'key_prefix': new_key_prefix
        })
        
    except APIKey.DoesNotExist:
        return Response({'error': 'API key not found'}, status=status.HTTP_404_NOT_FOUND)
