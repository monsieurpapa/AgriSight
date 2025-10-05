"""
API views for satellite data processing.
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from apps.geospatial.models import Region, SatelliteImage, VegetationIndex
from apps.analytics.models import AgriculturalStressEvent
from apps.organizations.models import Organization
from .tasks import (
    process_region_satellite_data,
    ingest_sentinel_data_periodic,
    generate_vegetation_trend_analysis,
    create_stress_alerts
)
from .processors import SatelliteDataProcessor


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def trigger_satellite_processing(request):
    """
    Trigger satellite data processing for a specific region.
    """
    region_id = request.data.get('region_id')
    start_date = request.data.get('start_date')
    end_date = request.data.get('end_date')
    
    if not all([region_id, start_date, end_date]):
        return Response(
            {'error': 'region_id, start_date, and end_date are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user has access to the region
    user = request.user
    if user.user_type != 'admin':
        if not user.organization or not Region.objects.filter(
            id=region_id,
            organizations=user.organization
        ).exists():
            return Response(
                {'error': 'Access denied to this region'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    try:
        # Start the processing task
        task = process_region_satellite_data.delay(region_id, start_date, end_date)
        
        return Response({
            'task_id': task.id,
            'status': 'Processing started',
            'message': f'Satellite data processing initiated for region {region_id}'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to start processing: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_processing_status(request, task_id):
    """
    Get the status of a satellite data processing task.
    """
    try:
        from celery.result import AsyncResult
        
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': task_result.state,
                'current': 0,
                'total': 100,
                'message': 'Task is waiting to be processed...'
            }
        elif task_result.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'status': task_result.state,
                'current': task_result.info.get('current', 0),
                'total': task_result.info.get('total', 100),
                'message': task_result.info.get('status', 'Processing...')
            }
        elif task_result.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'status': task_result.state,
                'current': 100,
                'total': 100,
                'message': 'Processing completed successfully',
                'result': task_result.result
            }
        else:  # FAILURE
            response = {
                'task_id': task_id,
                'status': task_result.state,
                'error': task_result.info.get('error', 'Unknown error occurred')
            }
        
        return Response(response)
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get task status: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_region_vegetation_data(request, region_id):
    """
    Get vegetation index data for a specific region.
    """
    # Check access permissions
    user = request.user
    if user.user_type != 'admin':
        if not user.organization or not Region.objects.filter(
            id=region_id,
            organizations=user.organization
        ).exists():
            return Response(
                {'error': 'Access denied to this region'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    try:
        region = Region.objects.get(id=region_id)
        
        # Get query parameters
        days_back = int(request.GET.get('days', 30))
        index_type = request.GET.get('index_type')
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Get vegetation indices
        queryset = VegetationIndex.objects.filter(
            satellite_image__region=region,
            satellite_image__acquisition_date__gte=start_date,
            satellite_image__is_processed=True
        )
        
        if index_type:
            queryset = queryset.filter(index_type=index_type)
        
        queryset = queryset.order_by('satellite_image__acquisition_date')
        
        # Format the data
        vegetation_data = []
        for index in queryset:
            vegetation_data.append({
                'id': str(index.id),
                'index_type': index.index_type,
                'date': index.satellite_image.acquisition_date.date().isoformat(),
                'mean_value': index.mean_value,
                'min_value': index.min_value,
                'max_value': index.max_value,
                'std_deviation': index.std_deviation,
                'satellite_image_id': str(index.satellite_image.id)
            })
        
        # Calculate summary statistics
        summary_stats = {}
        for index_type in ['NDVI', 'EVI', 'NDWI', 'SAVI']:
            type_data = [d for d in vegetation_data if d['index_type'] == index_type]
            if type_data:
                values = [d['mean_value'] for d in type_data]
                summary_stats[index_type] = {
                    'count': len(values),
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'latest': values[-1] if values else None
                }
        
        return Response({
            'region_id': region_id,
            'region_name': region.name,
            'data_period_days': days_back,
            'vegetation_data': vegetation_data,
            'summary_statistics': summary_stats,
            'total_records': len(vegetation_data)
        })
        
    except Region.DoesNotExist:
        return Response(
            {'error': 'Region not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get vegetation data: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_trend_analysis(request):
    """
    Generate vegetation trend analysis for a region.
    """
    region_id = request.data.get('region_id')
    months_back = request.data.get('months_back', 12)
    
    if not region_id:
        return Response(
            {'error': 'region_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check access permissions
    user = request.user
    if user.user_type != 'admin':
        if not user.organization or not Region.objects.filter(
            id=region_id,
            organizations=user.organization
        ).exists():
            return Response(
                {'error': 'Access denied to this region'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    try:
        # Start the trend analysis task
        task = generate_vegetation_trend_analysis.delay(region_id, months_back)
        
        return Response({
            'task_id': task.id,
            'status': 'Analysis started',
            'message': f'Vegetation trend analysis initiated for region {region_id}'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to start trend analysis: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_processing_statistics(request):
    """
    Get satellite data processing statistics.
    """
    user = request.user
    
    # Get accessible regions
    if user.user_type == 'admin':
        accessible_regions = Region.objects.all()
    elif user.organization:
        accessible_regions = Region.objects.filter(organizations=user.organization)
    else:
        accessible_regions = Region.objects.none()
    
    try:
        # Calculate statistics
        total_regions = accessible_regions.count()
        
        # Get satellite images for accessible regions
        satellite_images = SatelliteImage.objects.filter(
            region__in=accessible_regions
        )
        
        total_images = satellite_images.count()
        processed_images = satellite_images.filter(is_processed=True).count()
        
        # Get vegetation indices
        vegetation_indices = VegetationIndex.objects.filter(
            satellite_image__region__in=accessible_regions
        )
        
        total_indices = vegetation_indices.count()
        
        # Get stress events
        stress_events = AgriculturalStressEvent.objects.filter(
            region__in=accessible_regions
        )
        
        total_stress_events = stress_events.count()
        recent_stress_events = stress_events.filter(
            detection_date__gte=timezone.now().date() - timedelta(days=7)
        ).count()
        
        # Get processing status by region
        region_stats = []
        for region in accessible_regions:
            region_images = satellite_images.filter(region=region)
            region_stats.append({
                'region_id': str(region.id),
                'region_name': region.name,
                'total_images': region_images.count(),
                'processed_images': region_images.filter(is_processed=True).count(),
                'stress_events': stress_events.filter(region=region).count(),
                'last_processed': region_images.filter(is_processed=True)
                    .order_by('-acquisition_date')
                    .first()
                    .acquisition_date
                    .isoformat() if region_images.filter(is_processed=True).exists() else None
            })
        
        return Response({
            'overview': {
                'total_regions': total_regions,
                'total_images': total_images,
                'processed_images': processed_images,
                'processing_percentage': (processed_images / total_images * 100) if total_images > 0 else 0,
                'total_vegetation_indices': total_indices,
                'total_stress_events': total_stress_events,
                'recent_stress_events': recent_stress_events
            },
            'region_statistics': region_stats,
            'generated_at': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to get processing statistics: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def manual_data_ingestion(request):
    """
    Manually trigger satellite data ingestion for all regions.
    """
    # Only allow admins to trigger manual ingestion
    if request.user.user_type != 'admin':
        return Response(
            {'error': 'Only administrators can trigger manual data ingestion'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Start the ingestion task
        task = ingest_sentinel_data_periodic.delay()
        
        return Response({
            'task_id': task.id,
            'status': 'Ingestion started',
            'message': 'Manual satellite data ingestion initiated for all regions'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Failed to start data ingestion: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_satellite_image_details(request, image_id):
    """
    Get detailed information about a specific satellite image.
    """
    try:
        satellite_image = SatelliteImage.objects.get(id=image_id)
        
        # Check access permissions
        user = request.user
        if user.user_type != 'admin':
            if not user.organization or satellite_image.region not in Region.objects.filter(
                organizations=user.organization
            ):
                return Response(
                    {'error': 'Access denied to this satellite image'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get vegetation indices for this image
        vegetation_indices = VegetationIndex.objects.filter(
            satellite_image=satellite_image
        )
        
        indices_data = []
        for index in vegetation_indices:
            indices_data.append({
                'id': str(index.id),
                'index_type': index.index_type,
                'mean_value': index.mean_value,
                'min_value': index.min_value,
                'max_value': index.max_value,
                'std_deviation': index.std_deviation,
                'raster_path': index.raster_path
            })
        
        # Get associated stress events
        stress_events = AgriculturalStressEvent.objects.filter(
            evidence_indices__satellite_image=satellite_image
        )
        
        stress_events_data = []
        for event in stress_events:
            stress_events_data.append({
                'id': str(event.id),
                'stress_type': event.stress_type,
                'severity': event.severity,
                'detection_date': event.detection_date.isoformat(),
                'description': event.description
            })
        
        return Response({
            'satellite_image': {
                'id': str(satellite_image.id),
                'region_name': satellite_image.region.name,
                'acquisition_date': satellite_image.acquisition_date.isoformat(),
                'satellite_name': satellite_image.satellite_name,
                'cloud_cover_percentage': satellite_image.cloud_cover_percentage,
                'resolution_meters': satellite_image.resolution_meters,
                'bands_available': satellite_image.bands_available,
                'is_processed': satellite_image.is_processed,
                'processing_notes': satellite_image.processing_notes,
                'metadata': satellite_image.metadata,
                'created_at': satellite_image.created_at.isoformat(),
                'updated_at': satellite_image.updated_at.isoformat()
            },
            'vegetation_indices': indices_data,
            'stress_events': stress_events_data,
            'total_indices': len(indices_data),
            'total_stress_events': len(stress_events_data)
        })
        
    except SatelliteImage.DoesNotExist:
        return Response(
            {'error': 'Satellite image not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': f'Failed to get satellite image details: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
