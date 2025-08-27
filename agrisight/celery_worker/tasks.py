"""
Celery tasks for AgriSight platform.
"""

import os
import sys
import django
from celery import Celery
import numpy as np
import rasterio
from rasterio.mask import mask
from sklearn.ensemble import IsolationForest
import pandas as pd
from datetime import datetime, timedelta
import requests

# Setup Django
sys.path.append('/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrisight.settings')
django.setup()

from django.conf import settings
from apps.geospatial.models import SatelliteImage, VegetationIndex, Region
from apps.analytics.models import AgriculturalStressEvent
from apps.reports_alerts.models import Alert

# Initialize Celery
app = Celery('agrisight')
app.config_from_object('django.conf:settings', namespace='CELERY')


@app.task(bind=True)
def process_satellite_image(self, satellite_image_id):
    """
    Process a satellite image to calculate vegetation indices.
    """
    try:
        satellite_image = SatelliteImage.objects.get(id=satellite_image_id)
        
        # Simulate image processing (in real implementation, this would load actual satellite data)
        # For demo purposes, we'll create mock vegetation indices
        
        indices_to_calculate = ['NDVI', 'EVI', 'NDWI', 'SAVI']
        
        for index_type in indices_to_calculate:
            # Simulate calculation with random but realistic values
            if index_type == 'NDVI':
                mean_val = np.random.uniform(0.2, 0.8)
                min_val = max(0, mean_val - 0.3)
                max_val = min(1, mean_val + 0.3)
            elif index_type == 'EVI':
                mean_val = np.random.uniform(0.1, 0.6)
                min_val = max(0, mean_val - 0.2)
                max_val = min(1, mean_val + 0.2)
            elif index_type == 'NDWI':
                mean_val = np.random.uniform(-0.5, 0.5)
                min_val = max(-1, mean_val - 0.3)
                max_val = min(1, mean_val + 0.3)
            else:  # SAVI
                mean_val = np.random.uniform(0.1, 0.7)
                min_val = max(0, mean_val - 0.2)
                max_val = min(1, mean_val + 0.2)
            
            std_dev = (max_val - min_val) / 4
            
            # Create or update vegetation index
            vegetation_index, created = VegetationIndex.objects.get_or_create(
                satellite_image=satellite_image,
                index_type=index_type,
                defaults={
                    'mean_value': mean_val,
                    'min_value': min_val,
                    'max_value': max_val,
                    'std_deviation': std_dev,
                    'raster_path': f'/data/indices/{satellite_image_id}_{index_type}.tif'
                }
            )
        
        # Mark image as processed
        satellite_image.is_processed = True
        satellite_image.processing_notes = f"Processed on {datetime.now()}"
        satellite_image.save()
        
        # Trigger anomaly detection
        detect_anomalies.delay(satellite_image_id)
        
        return f"Successfully processed satellite image {satellite_image_id}"
        
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


@app.task(bind=True)
def detect_anomalies(self, satellite_image_id):
    """
    Detect anomalies in vegetation indices compared to historical data.
    """
    try:
        satellite_image = SatelliteImage.objects.get(id=satellite_image_id)
        region = satellite_image.region
        
        # Get historical NDVI data for the region
        historical_images = SatelliteImage.objects.filter(
            region=region,
            is_processed=True,
            acquisition_date__lt=satellite_image.acquisition_date,
            acquisition_date__gte=satellite_image.acquisition_date - timedelta(days=365)
        ).order_by('-acquisition_date')[:20]  # Last 20 images
        
        if len(historical_images) < 5:
            return "Not enough historical data for anomaly detection"
        
        # Get NDVI values
        current_ndvi = VegetationIndex.objects.filter(
            satellite_image=satellite_image,
            index_type='NDVI'
        ).first()
        
        if not current_ndvi:
            return "No NDVI data available for current image"
        
        historical_ndvi_values = []
        for img in historical_images:
            ndvi = VegetationIndex.objects.filter(
                satellite_image=img,
                index_type='NDVI'
            ).first()
            if ndvi:
                historical_ndvi_values.append(ndvi.mean_value)
        
        if len(historical_ndvi_values) < 5:
            return "Insufficient historical NDVI data"
        
        # Simple anomaly detection using statistical threshold
        historical_mean = np.mean(historical_ndvi_values)
        historical_std = np.std(historical_ndvi_values)
        threshold = 2 * historical_std  # 2 standard deviations
        
        deviation = abs(current_ndvi.mean_value - historical_mean)
        
        if deviation > threshold:
            # Create stress event
            stress_type = 'water' if current_ndvi.mean_value < historical_mean else 'other'
            severity = min(5, max(1, int(deviation / historical_std)))
            
            stress_event = AgriculturalStressEvent.objects.create(
                region=region,
                detection_date=satellite_image.acquisition_date.date(),
                stress_type=stress_type,
                severity=severity,
                affected_area_hectares=region.area_hectares * 0.1,  # Assume 10% affected
                description=f"Anomalous NDVI detected: {current_ndvi.mean_value:.3f} vs historical mean {historical_mean:.3f}",
                geometry=region.geometry
            )
            
            stress_event.evidence_indices.add(current_ndvi)
            
            # Create alerts for organizations with access to this region
            for org in region.organizations.all():
                Alert.objects.create(
                    organization=org,
                    alert_type='stress',
                    severity='warning' if severity <= 3 else 'critical',
                    title=f"Agricultural Stress Detected in {region.name}",
                    message=f"Anomalous vegetation index detected with severity level {severity}",
                    related_stress_event=stress_event
                )
                alert.regions.add(region)
        
        return f"Anomaly detection completed for image {satellite_image_id}"
        
    except Exception as exc:
        self.retry(exc=exc, countdown=60, max_retries=3)


@app.task
def ingest_sentinel_data():
    """
    Periodic task to ingest new Sentinel-2 data.
    This is a placeholder for actual satellite data ingestion.
    """
    try:
        # In a real implementation, this would:
        # 1. Query Sentinel Hub or Copernicus API for new data
        # 2. Download relevant tiles for monitored regions
        # 3. Create SatelliteImage records
        # 4. Trigger processing tasks
        
        regions = Region.objects.all()
        
        for region in regions:
            # Simulate finding new satellite data
            if np.random.random() > 0.7:  # 30% chance of new data
                # Create mock satellite image record
                satellite_image = SatelliteImage.objects.create(
                    region=region,
                    acquisition_date=datetime.now(),
                    satellite_name='Sentinel-2',
                    cloud_cover_percentage=np.random.uniform(0, 30),
                    resolution_meters=10.0,
                    bands_available=['B02', 'B03', 'B04', 'B08', 'B11', 'B12'],
                    image_path=f'/data/sentinel2/{region.id}/{datetime.now().strftime("%Y%m%d")}.tif'
                )
                
                # Trigger processing
                process_satellite_image.delay(str(satellite_image.id))
        
        return f"Sentinel data ingestion completed for {len(regions)} regions"
        
    except Exception as exc:
        return f"Error in Sentinel data ingestion: {str(exc)}"


@app.task
def generate_periodic_reports():
    """
    Generate periodic reports for organizations.
    """
    try:
        from apps.organizations.models import Organization
        from apps.reports_alerts.models import Report
        
        organizations = Organization.objects.filter(is_active=True)
        
        for org in organizations:
            # Get regions accessible to this organization
            accessible_regions = Region.objects.filter(organizations=org)
            
            if accessible_regions.exists():
                # Create weekly report
                report = Report.objects.create(
                    title=f"Weekly Agricultural Monitoring Report - {datetime.now().strftime('%Y-%m-%d')}",
                    organization=org,
                    report_type='crop_health',
                    time_period_start=(datetime.now() - timedelta(days=7)).date(),
                    time_period_end=datetime.now().date(),
                    content={
                        'summary': 'Weekly crop health analysis',
                        'regions_monitored': list(accessible_regions.values_list('name', flat=True)),
                        'total_area_hectares': sum(accessible_regions.values_list('area_hectares', flat=True)),
                        'generated_at': datetime.now().isoformat()
                    },
                    file_path=f'/data/reports/{org.id}/weekly_{datetime.now().strftime("%Y%m%d")}.pdf'
                )
                
                report.regions.set(accessible_regions)
        
        return f"Generated periodic reports for {len(organizations)} organizations"
        
    except Exception as exc:
        return f"Error generating periodic reports: {str(exc)}"


# Register periodic tasks
app.conf.beat_schedule = {
    'ingest-sentinel-data': {
        'task': 'tasks.ingest_sentinel_data',
        'schedule': 3600.0,  # Every hour
    },
    'generate-periodic-reports': {
        'task': 'tasks.generate_periodic_reports',
        'schedule': 86400.0,  # Daily
    },
}

app.conf.timezone = 'UTC'

