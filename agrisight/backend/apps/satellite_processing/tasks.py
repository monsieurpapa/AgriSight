"""
Celery tasks for real satellite data processing.
Replaces mock implementations with actual satellite data processing.
"""

from celery import shared_task
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List
from django.utils import timezone

from .processors import SatelliteDataProcessor
from apps.geospatial.models import Region, SatelliteImage
from apps.analytics.models import AgriculturalStressEvent
from apps.reports_alerts.models import Alert

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_region_satellite_data(self, region_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """
    Process satellite data for a specific region and time period.
    
    Args:
        region_id: ID of the region to process
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        Dict with processing results
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting satellite data processing...'}
        )
        
        processor = SatelliteDataProcessor()
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 25, 'total': 100, 'status': 'Fetching satellite data from Sentinel Hub...'}
        )
        
        # Process the region data
        result = processor.process_region_satellite_data(region_id, start_date, end_date)
        
        self.update_state(
            state='PROGRESS',
            meta={'current': 75, 'total': 100, 'status': 'Analyzing vegetation indices...'}
        )
        
        # Update processing status
        if result.get('success', False):
            self.update_state(
                state='PROGRESS',
                meta={'current': 90, 'total': 100, 'status': 'Creating alerts and notifications...'}
            )
            
            # Create alerts for detected stress events
            if result.get('stress_events_detected', 0) > 0:
                create_stress_alerts.delay(region_id, result['stress_events_detected'])
            
            self.update_state(
                state='SUCCESS',
                meta={'current': 100, 'total': 100, 'status': 'Processing completed successfully'}
            )
        else:
            self.update_state(
                state='FAILURE',
                meta={'error': result.get('error', 'Unknown error occurred')}
            )
        
        return result
        
    except Exception as exc:
        logger.error(f"Error in satellite data processing task: {str(exc)}")
        self.retry(countdown=60, exc=exc)


@shared_task(bind=True, max_retries=3)
def ingest_sentinel_data_periodic(self) -> Dict[str, Any]:
    """
    Periodic task to ingest new Sentinel-2 data for all active regions.
    Runs every hour to check for new satellite data.
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'current': 0, 'total': 100, 'status': 'Starting periodic satellite data ingestion...'}
        )
        
        # Get all active regions
        regions = Region.objects.all()
        processed_regions = 0
        total_images = 0
        total_stress_events = 0
        
        processor = SatelliteDataProcessor()
        
        for i, region in enumerate(regions):
            try:
                # Check if we need to process this region
                last_processed = SatelliteImage.objects.filter(
                    region=region,
                    is_processed=True
                ).order_by('-acquisition_date').first()
                
                # If no recent data or data is older than 7 days, process new data
                should_process = (
                    last_processed is None or 
                    last_processed.acquisition_date < timezone.now() - timedelta(days=7)
                )
                
                if should_process:
                    # Define date range for processing (last 14 days)
                    end_date = datetime.now().strftime('%Y-%m-%d')
                    start_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
                    
                    self.update_state(
                        state='PROGRESS',
                        meta={
                            'current': int((i / len(regions)) * 80),
                            'total': 100,
                            'status': f'Processing region: {region.name}'
                        }
                    )
                    
                    result = processor.process_region_satellite_data(
                        str(region.id), start_date, end_date
                    )
                    
                    if result.get('success', False):
                        processed_regions += 1
                        total_images += result.get('images_processed', 0)
                        total_stress_events += result.get('stress_events_detected', 0)
                        
                        # Trigger async processing for stress events
                        if result.get('stress_events_detected', 0) > 0:
                            create_stress_alerts.delay(str(region.id), result['stress_events_detected'])
                
            except Exception as e:
                logger.error(f"Error processing region {region.name}: {str(e)}")
                continue
        
        self.update_state(
            state='SUCCESS',
            meta={
                'current': 100,
                'total': 100,
                'status': 'Periodic ingestion completed',
                'processed_regions': processed_regions,
                'total_images': total_images,
                'total_stress_events': total_stress_events
            }
        )
        
        return {
            'processed_regions': processed_regions,
            'total_images': total_images,
            'total_stress_events': total_stress_events,
            'success': True
        }
        
    except Exception as exc:
        logger.error(f"Error in periodic satellite data ingestion: {str(exc)}")
        self.retry(countdown=300, exc=exc)  # Retry after 5 minutes


@shared_task
def create_stress_alerts(region_id: str, stress_event_count: int) -> Dict[str, Any]:
    """
    Create alerts for detected agricultural stress events.
    
    Args:
        region_id: ID of the region where stress was detected
        stress_event_count: Number of stress events detected
        
    Returns:
        Dict with alert creation results
    """
    try:
        region = Region.objects.get(id=region_id)
        
        # Get recent stress events for this region
        recent_stress_events = AgriculturalStressEvent.objects.filter(
            region=region,
            detection_date__gte=timezone.now().date()
        ).order_by('-detection_date')[:stress_event_count]
        
        alerts_created = 0
        
        for stress_event in recent_stress_events:
            # Create alerts for organizations with access to this region
            for org in region.organizations.all():
                # Determine alert severity based on stress event severity
                if stress_event.severity >= 4:
                    alert_severity = 'critical'
                elif stress_event.severity >= 3:
                    alert_severity = 'warning'
                else:
                    alert_severity = 'info'
                
                alert = Alert.objects.create(
                    organization=org,
                    alert_type='agricultural_stress',
                    severity=alert_severity,
                    title=f"Agricultural Stress Detected in {region.name}",
                    message=f"{stress_event.stress_type.title()} stress detected with severity level {stress_event.severity}. "
                           f"Affected area: {stress_event.affected_area_hectares:.1f} hectares. "
                           f"Description: {stress_event.description}",
                    related_stress_event=stress_event,
                    is_read=False
                )
                alert.regions.add(region)
                alerts_created += 1
        
        logger.info(f"Created {alerts_created} alerts for {stress_event_count} stress events in region {region.name}")
        
        return {
            'alerts_created': alerts_created,
            'region_name': region.name,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error creating stress alerts: {str(e)}")
        return {'error': str(e), 'success': False}


@shared_task
def cleanup_old_satellite_data() -> Dict[str, Any]:
    """
    Cleanup old satellite data and temporary files to manage storage.
    """
    try:
        from django.db.models import Q
        
        # Delete satellite images older than 1 year that are not marked as important
        cutoff_date = timezone.now() - timedelta(days=365)
        
        old_images = SatelliteImage.objects.filter(
            acquisition_date__lt=cutoff_date,
            is_processed=True
        ).exclude(
            # Keep images that have associated stress events
            vegetation_indices__satellite_image__analytics_agriculturalstressevent__isnull=False
        )
        
        deleted_count = 0
        for image in old_images:
            try:
                # Delete associated vegetation indices
                image.vegetation_indices.all().delete()
                
                # Delete the satellite image
                image.delete()
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Error deleting satellite image {image.id}: {str(e)}")
                continue
        
        # Clean up temporary processing files older than 7 days
        import os
        import glob
        temp_dir = '/tmp/agrisight_processing'
        if os.path.exists(temp_dir):
            temp_files = glob.glob(f"{temp_dir}/*.tif")
            cleaned_files = 0
            
            for temp_file in temp_files:
                try:
                    file_age = datetime.now() - datetime.fromtimestamp(os.path.getctime(temp_file))
                    if file_age.days > 7:
                        os.remove(temp_file)
                        cleaned_files += 1
                except Exception as e:
                    logger.error(f"Error deleting temp file {temp_file}: {str(e)}")
        
        return {
            'deleted_images': deleted_count,
            'cleaned_temp_files': cleaned_files,
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")
        return {'error': str(e), 'success': False}


@shared_task
def generate_vegetation_trend_analysis(region_id: str, months_back: int = 12) -> Dict[str, Any]:
    """
    Generate comprehensive vegetation trend analysis for a region.
    
    Args:
        region_id: ID of the region to analyze
        months_back: Number of months to look back for trend analysis
        
    Returns:
        Dict with trend analysis results
    """
    try:
        region = Region.objects.get(id=region_id)
        
        # Get vegetation indices for the specified period
        start_date = timezone.now() - timedelta(days=months_back * 30)
        
        vegetation_data = {}
        
        # Get data for each vegetation index type
        for index_type in ['NDVI', 'EVI', 'NDWI', 'SAVI']:
            indices = VegetationIndex.objects.filter(
                satellite_image__region=region,
                satellite_image__acquisition_date__gte=start_date,
                index_type=index_type
            ).order_by('satellite_image__acquisition_date')
            
            if indices.exists():
                vegetation_data[index_type] = [
                    {
                        'date': index.satellite_image.acquisition_date.date().isoformat(),
                        'mean_value': index.mean_value,
                        'min_value': index.min_value,
                        'max_value': index.max_value,
                        'std_deviation': index.std_deviation
                    }
                    for index in indices
                ]
        
        # Calculate trends
        trends = {}
        for index_type, data in vegetation_data.items():
            if len(data) >= 3:  # Need at least 3 data points for trend
                values = [d['mean_value'] for d in data]
                dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data]
                
                # Simple linear trend calculation
                x = [(d - dates[0]).days for d in dates]
                y = values
                
                if len(x) > 1:
                    slope = (len(x) * sum(x[i] * y[i] for i in range(len(x))) - sum(x) * sum(y)) / \
                           (len(x) * sum(xi**2 for xi in x) - sum(x)**2)
                    
                    trends[index_type] = {
                        'slope': slope,
                        'trend_direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
                        'data_points': len(data),
                        'latest_value': values[-1] if values else None,
                        'earliest_value': values[0] if values else None
                    }
        
        # Determine overall vegetation health trend
        overall_trend = 'stable'
        if trends:
            ndvi_trend = trends.get('NDVI', {})
            if ndvi_trend.get('trend_direction') == 'decreasing':
                overall_trend = 'declining'
            elif ndvi_trend.get('trend_direction') == 'increasing':
                overall_trend = 'improving'
        
        return {
            'region_id': region_id,
            'region_name': region.name,
            'analysis_period_months': months_back,
            'vegetation_data': vegetation_data,
            'trends': trends,
            'overall_trend': overall_trend,
            'analysis_date': timezone.now().isoformat(),
            'success': True
        }
        
    except Exception as e:
        logger.error(f"Error generating vegetation trend analysis: {str(e)}")
        return {'error': str(e), 'success': False}


# Update the beat schedule for the new tasks
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'ingest-sentinel-data': {
        'task': 'apps.satellite_processing.tasks.ingest_sentinel_data_periodic',
        'schedule': crontab(minute=0),  # Run every hour
    },
    'cleanup-old-data': {
        'task': 'apps.satellite_processing.tasks.cleanup_old_satellite_data',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}
