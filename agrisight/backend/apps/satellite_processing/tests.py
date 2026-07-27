"""
Comprehensive tests for satellite data processing functionality.
"""

import os
import tempfile
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.geospatial.models import Region, SatelliteImage, VegetationIndex
from apps.analytics.models import AgriculturalStressEvent
from apps.organizations.models import Organization
from .models import BatchJob
from .processors import SatelliteDataProcessor, VegetationIndexCalculator
from .tasks import (
    process_region_satellite_data,
    create_stress_alerts,
    generate_vegetation_trend_analysis,
    monitor_batch_jobs,
    _ingest_batch_job_outputs,
)

User = get_user_model()


class VegetationIndexCalculatorTest(TestCase):
    """Test vegetation index calculation functions."""
    
    def setUp(self):
        """Set up test data."""
        self.nir_band = np.array([[0.8, 0.7, 0.6], [0.9, 0.8, 0.7]])
        self.red_band = np.array([[0.3, 0.4, 0.5], [0.2, 0.3, 0.4]])
        self.green_band = np.array([[0.4, 0.5, 0.6], [0.3, 0.4, 0.5]])
        self.blue_band = np.array([[0.2, 0.3, 0.4], [0.1, 0.2, 0.3]])
    
    def test_calculate_ndvi(self):
        """Test NDVI calculation."""
        ndvi = VegetationIndexCalculator.calculate_ndvi(self.nir_band, self.red_band)
        
        # NDVI should be between -1 and 1
        self.assertTrue(np.all(ndvi >= -1))
        self.assertTrue(np.all(ndvi <= 1))
        
        # Test specific calculation
        expected = (self.nir_band - self.red_band) / (self.nir_band + self.red_band)
        np.testing.assert_array_almost_equal(ndvi, expected)
    
    def test_calculate_evi(self):
        """Test EVI calculation."""
        evi = VegetationIndexCalculator.calculate_evi(self.nir_band, self.red_band, self.blue_band)
        
        # EVI should be between -1 and 1
        self.assertTrue(np.all(evi >= -1))
        self.assertTrue(np.all(evi <= 1))
    
    def test_calculate_ndwi(self):
        """Test NDWI calculation."""
        ndwi = VegetationIndexCalculator.calculate_ndwi(self.green_band, self.nir_band)
        
        # NDWI should be between -1 and 1
        self.assertTrue(np.all(ndwi >= -1))
        self.assertTrue(np.all(ndwi <= 1))
    
    def test_calculate_savi(self):
        """Test SAVI calculation."""
        savi = VegetationIndexCalculator.calculate_savi(self.nir_band, self.red_band)
        
        # SAVI should be between -1 and 1
        self.assertTrue(np.all(savi >= -1))
        self.assertTrue(np.all(savi <= 1))
    
    def test_calculate_all_indices(self):
        """Test calculation of all vegetation indices."""
        bands = {
            'B02': self.blue_band,
            'B03': self.green_band,
            'B04': self.red_band,
            'B08': self.nir_band
        }
        
        indices = VegetationIndexCalculator.calculate_all_indices(bands)
        
        # Should calculate all available indices
        self.assertIn('NDVI', indices)
        self.assertIn('EVI', indices)
        self.assertIn('NDWI', indices)
        self.assertIn('SAVI', indices)
        
        # All indices should have correct shape
        for index_name, index_array in indices.items():
            self.assertEqual(index_array.shape, self.nir_band.shape)
    
    def test_division_by_zero_handling(self):
        """Test handling of division by zero."""
        zero_band = np.zeros_like(self.nir_band)
        
        # Should not raise exception
        ndvi = VegetationIndexCalculator.calculate_ndvi(zero_band, zero_band)
        self.assertTrue(np.all(np.isnan(ndvi)))


class SatelliteDataProcessorTest(TestCase):
    """Test satellite data processing functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            organization_type='humanitarian',
            contact_email='test@example.com'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        self.region = Region.objects.create(
            name='Test Region',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )
        
        self.region.organizations.add(self.organization)
        
        self.processor = SatelliteDataProcessor()
    
    @patch('apps.satellite_processing.processors.SentinelHubClient')
    def test_process_region_satellite_data_success(self, mock_client_class):
        """Test successful satellite data processing."""
        # Mock Sentinel Hub client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock API responses
        mock_client.get_true_color_image.return_value.status_code = 200
        mock_client.get_vegetation_index.return_value.status_code = 200
        mock_client.get_vegetation_index.return_value.content = b'mock_tiff_data'
        
        # Process region data
        result = self.processor.process_region_satellite_data(
            str(self.region.id),
            '2024-01-01',
            '2024-01-07'
        )
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['region_id'], str(self.region.id))
        self.assertGreater(result['images_processed'], 0)
    
    @patch('apps.satellite_processing.processors.SentinelHubClient')
    def test_process_region_satellite_data_no_data(self, mock_client_class):
        """Test satellite data processing when no data is available."""
        # Mock Sentinel Hub client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Mock API responses to return no data
        mock_client.get_true_color_image.return_value.status_code = 404
        
        # Process region data
        result = self.processor.process_region_satellite_data(
            str(self.region.id),
            '2024-01-01',
            '2024-01-07'
        )
        
        # Check result
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_geometry_to_bbox(self):
        """Test geometry to bounding box conversion."""
        bbox = self.processor._geometry_to_bbox(self.region.geometry)
        
        # Should return 4 coordinates
        self.assertEqual(len(bbox), 4)
        self.assertIsInstance(bbox[0], float)
        self.assertIsInstance(bbox[1], float)
        self.assertIsInstance(bbox[2], float)
        self.assertIsInstance(bbox[3], float)
    
    def test_calculate_raster_statistics(self):
        """Test raster statistics calculation."""
        # Create a temporary raster file
        with tempfile.NamedTemporaryFile(suffix='.tif', delete=False) as temp_file:
            # Create a simple test array
            test_data = np.random.uniform(0, 1, (100, 100))
            
            # Save as a simple binary file (simplified for testing)
            temp_file.write(test_data.astype(np.float32).tobytes())
            temp_file_path = temp_file.name
        
        try:
            # Mock rasterio to return test data
            with patch('rasterio.open') as mock_open:
                mock_src = MagicMock()
                mock_src.read.return_value = [test_data]
                mock_open.return_value.__enter__.return_value = mock_src
                
                stats = self.processor._calculate_raster_statistics(temp_file_path)
                
                # Check statistics
                self.assertIn('mean', stats)
                self.assertIn('min', stats)
                self.assertIn('max', stats)
                self.assertIn('std', stats)
                
                self.assertGreaterEqual(stats['mean'], 0)
                self.assertLessEqual(stats['mean'], 1)
        
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_determine_stress_type(self):
        """Test stress type determination."""
        # Test water stress (low NDVI)
        stress_type = self.processor._determine_stress_type('NDVI', 0.3, 0.6)
        self.assertEqual(stress_type, 'water')
        
        # Test nutrient stress (moderate NDVI)
        stress_type = self.processor._determine_stress_type('NDVI', 0.5, 0.6)
        self.assertEqual(stress_type, 'nutrient')
        
        # Test disease stress (low EVI)
        stress_type = self.processor._determine_stress_type('EVI', 0.3, 0.5)
        self.assertEqual(stress_type, 'disease')
        
        # Test other stress
        stress_type = self.processor._determine_stress_type('UNKNOWN', 0.5, 0.6)
        self.assertEqual(stress_type, 'other')


class SatelliteProcessingTasksTest(TestCase):
    """Test Celery tasks for satellite processing."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            organization_type='humanitarian',
            contact_email='test@example.com'
        )
        
        self.region = Region.objects.create(
            name='Test Region',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )
        
        self.region.organizations.add(self.organization)
        
        # Create a satellite image
        self.satellite_image = SatelliteImage.objects.create(
            region=self.region,
            acquisition_date=timezone.now(),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=10.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path.tif',
            is_processed=True
        )
        
        # Create vegetation indices
        self.ndvi_index = VegetationIndex.objects.create(
            satellite_image=self.satellite_image,
            index_type='NDVI',
            mean_value=0.65,
            min_value=0.2,
            max_value=0.9,
            std_deviation=0.15,
            raster_path='/test/ndvi.tif'
        )
    
    @patch('apps.satellite_processing.tasks.SatelliteDataProcessor')
    def test_process_region_satellite_data_task(self, mock_processor_class):
        """Test the satellite data processing Celery task."""
        # Mock processor
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor.process_region_satellite_data.return_value = {
            'success': True,
            'images_processed': 1,
            'stress_events_detected': 0
        }
        
        # Run task
        result = process_region_satellite_data(
            str(self.region.id),
            '2024-01-01',
            '2024-01-07'
        )
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['images_processed'], 1)
    
    def test_create_stress_alerts_task(self):
        """Test stress alert creation task."""
        # Create a stress event
        stress_event = AgriculturalStressEvent.objects.create(
            region=self.region,
            detection_date=timezone.now().date(),
            stress_type='water',
            severity=3,
            affected_area_hectares=100.0,
            description='Test stress event',
            geometry=self.region.geometry
        )
        
        # Run task
        result = create_stress_alerts(str(self.region.id), 1)
        
        # Check result
        self.assertTrue(result['success'])
        self.assertGreater(result['alerts_created'], 0)
    
    def test_generate_vegetation_trend_analysis_task(self):
        """Test vegetation trend analysis task."""
        # Create additional historical data
        for i in range(5):
            historical_image = SatelliteImage.objects.create(
                region=self.region,
                acquisition_date=timezone.now() - timedelta(days=i*30),
                satellite_name='Sentinel-2',
                cloud_cover_percentage=10.0,
                resolution_meters=10.0,
                bands_available=['B02', 'B03', 'B04', 'B08'],
                image_path=f'/test/historical_{i}.tif',
                is_processed=True
            )
            
            VegetationIndex.objects.create(
                satellite_image=historical_image,
                index_type='NDVI',
                mean_value=0.6 + (i * 0.02),  # Slightly increasing trend
                min_value=0.2,
                max_value=0.9,
                std_deviation=0.15,
                raster_path=f'/test/historical_ndvi_{i}.tif'
            )
        
        # Run task
        result = generate_vegetation_trend_analysis(str(self.region.id), 6)
        
        # Check result
        self.assertTrue(result['success'])
        self.assertIn('trends', result)
        self.assertIn('NDVI', result['trends'])


class SatelliteProcessingViewsTest(TestCase):
    """Test API views for satellite processing."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            organization_type='humanitarian',
            contact_email='test@example.com'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='admin'
        )
        
        self.region = Region.objects.create(
            name='Test Region',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )
        
        self.region.organizations.add(self.organization)
    
    def test_trigger_satellite_processing_success(self):
        """Test successful satellite processing trigger."""
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        client.force_login(self.user)
        
        # Mock the Celery task
        with patch('apps.satellite_processing.views.process_region_satellite_data.delay') as mock_task:
            mock_task.return_value.id = 'test-task-id'
            
            response = client.post('/api/satellite-processing/process/', {
                'region_id': str(self.region.id),
                'start_date': '2024-01-01',
                'end_date': '2024-01-07'
            })
            
            self.assertEqual(response.status_code, 200)
            self.assertIn('task_id', response.json())
            self.assertEqual(response.json()['task_id'], 'test-task-id')
    
    def test_trigger_satellite_processing_missing_data(self):
        """Test satellite processing trigger with missing data."""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        response = client.post('/api/satellite-processing/process/', {
            'region_id': str(self.region.id),
            # Missing start_date and end_date
        })
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())
    
    def test_get_processing_statistics(self):
        """Test getting processing statistics."""
        from django.test import Client
        
        client = Client()
        client.force_login(self.user)
        
        # Create some test data
        satellite_image = SatelliteImage.objects.create(
            region=self.region,
            acquisition_date=timezone.now(),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=10.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path.tif',
            is_processed=True
        )
        
        VegetationIndex.objects.create(
            satellite_image=satellite_image,
            index_type='NDVI',
            mean_value=0.65,
            min_value=0.2,
            max_value=0.9,
            std_deviation=0.15,
            raster_path='/test/ndvi.tif'
        )
        
        response = client.get('/api/satellite-processing/statistics/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('overview', data)
        self.assertIn('region_statistics', data)
        self.assertGreater(data['overview']['total_regions'], 0)

    def test_processing_statistics_scoped_to_organization(self):
        """Test processing statistics are scoped to organization."""
        from django.test import Client

        org_a = Organization.objects.create(
            name='Org A',
            organization_type='humanitarian',
            contact_email='a@example.com'
        )
        org_b = Organization.objects.create(
            name='Org B',
            organization_type='cooperative',
            contact_email='b@example.com'
        )

        user = User.objects.create_user(
            username='orguser',
            email='orguser@example.com',
            password='testpass123',
            user_type='humanitarian',
            organization=org_a
        )

        region_a = Region.objects.create(
            name='Region A',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )
        region_b = Region.objects.create(
            name='Region B',
            country='DRC',
            province='South Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )

        region_a.organizations.add(org_a)
        region_b.organizations.add(org_b)

        SatelliteImage.objects.create(
            region=region_a,
            acquisition_date=timezone.now(),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=10.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path_a.tif',
            is_processed=True
        )
        SatelliteImage.objects.create(
            region=region_b,
            acquisition_date=timezone.now(),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=10.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path_b.tif',
            is_processed=True
        )

        client = Client()
        client.force_login(user)

        response = client.get('/api/v1/satellite-processing/statistics/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['overview']['total_regions'], 1)
        self.assertEqual(len(data['region_statistics']), 1)

    def test_trend_analysis_scoped_to_region(self):
        """Test trend analysis respects region access."""
        from django.test import Client

        org_a = Organization.objects.create(
            name='Org A',
            organization_type='humanitarian',
            contact_email='a@example.com'
        )
        org_b = Organization.objects.create(
            name='Org B',
            organization_type='cooperative',
            contact_email='b@example.com'
        )

        user = User.objects.create_user(
            username='orguser',
            email='orguser@example.com',
            password='testpass123',
            user_type='humanitarian',
            organization=org_a
        )

        region_a = Region.objects.create(
            name='Region A',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )
        region_b = Region.objects.create(
            name='Region B',
            country='DRC',
            province='South Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )

        region_a.organizations.add(org_a)
        region_b.organizations.add(org_b)

        image_a = SatelliteImage.objects.create(
            region=region_a,
            acquisition_date=timezone.now() - timedelta(days=2),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=10.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path_a.tif',
            is_processed=True
        )
        VegetationIndex.objects.create(
            satellite_image=image_a,
            index_type='NDVI',
            mean_value=0.65,
            min_value=0.2,
            max_value=0.9,
            std_deviation=0.15,
            raster_path='/test/ndvi_a.tif'
        )

        image_b = SatelliteImage.objects.create(
            region=region_b,
            acquisition_date=timezone.now() - timedelta(days=2),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=10.0,
            resolution_meters=10.0,
            bands_available=['B02', 'B03', 'B04', 'B08'],
            image_path='/test/path_b.tif',
            is_processed=True
        )
        VegetationIndex.objects.create(
            satellite_image=image_b,
            index_type='NDVI',
            mean_value=0.55,
            min_value=0.2,
            max_value=0.9,
            std_deviation=0.15,
            raster_path='/test/ndvi_b.tif'
        )

        client = Client()
        client.force_login(user)

        response = client.get(f'/api/v1/satellite-processing/trend-analysis/?days=30&region_id={region_a.id}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) >= 1)

        forbidden = client.get(f'/api/v1/satellite-processing/trend-analysis/?days=30&region_id={region_b.id}')
        self.assertEqual(forbidden.status_code, 403)


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class SatelliteProcessingIntegrationTest(TestCase):
    """Integration tests for satellite processing."""
    
    def setUp(self):
        """Set up test data."""
        self.organization = Organization.objects.create(
            name='Test Organization',
            organization_type='humanitarian',
            contact_email='test@example.com'
        )
        
        self.region = Region.objects.create(
            name='Test Region',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )
        
        self.region.organizations.add(self.organization)
    
    @patch('apps.satellite_processing.processors.SentinelHubClient')
    def test_end_to_end_processing(self, mock_client_class):
        """Test end-to-end satellite data processing."""
        # Mock Sentinel Hub client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_true_color_image.return_value.status_code = 200
        mock_client.get_vegetation_index.return_value.status_code = 200
        mock_client.get_vegetation_index.return_value.content = b'mock_tiff_data'
        
        # Process region data
        result = process_region_satellite_data(
            str(self.region.id),
            '2024-01-01',
            '2024-01-07'
        )
        
        # Check that satellite images were created
        satellite_images = SatelliteImage.objects.filter(region=self.region)
        self.assertGreater(satellite_images.count(), 0)
        
        # Check that vegetation indices were created
        vegetation_indices = VegetationIndex.objects.filter(
            satellite_image__region=self.region
        )
        self.assertGreater(vegetation_indices.count(), 0)
        
        # Check processing result
        self.assertTrue(result['success'])


class MonitorBatchJobsTest(TestCase):
    """Test the monitor_batch_jobs periodic task's status transitions."""

    def setUp(self):
        self.region = Region.objects.create(
            name='Test Region',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )

    def _make_job(self, status, request_id='req-1'):
        return BatchJob.objects.create(
            request_id=request_id,
            region=self.region,
            status=status,
            bbox=[28.5, -1.5, 30.0, 0.5],
            time_range_start=timezone.make_aware(datetime(2024, 1, 1)),
            time_range_end=timezone.make_aware(datetime(2024, 1, 31)),
            s3_bucket='test-bucket'
        )

    @patch('apps.satellite_processing.tasks.BatchClient')
    def test_analysis_done_triggers_start(self, mock_client_class):
        """ANALYSIS_DONE should call execute_start and optimistically move to PROCESSING."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_request_status.return_value = 'ANALYSIS_DONE'

        job = self._make_job('ANALYSING')

        monitor_batch_jobs()

        mock_client.execute_start.assert_called_once_with('req-1')
        job.refresh_from_db()
        self.assertEqual(job.status, 'PROCESSING')

    @patch('apps.satellite_processing.tasks._ingest_batch_job_outputs')
    @patch('apps.satellite_processing.tasks.BatchClient')
    def test_done_triggers_ingestion_and_records_tile_count(self, mock_client_class, mock_ingest):
        """DONE should ingest outputs and persist the count on the job."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_request_status.return_value = 'DONE'
        mock_ingest.return_value = 3

        job = self._make_job('PROCESSING')

        monitor_batch_jobs()

        mock_ingest.assert_called_once()
        job.refresh_from_db()
        self.assertEqual(job.status, 'DONE')
        self.assertEqual(job.tile_count, 3)

    @patch('apps.satellite_processing.tasks.BatchClient')
    def test_terminal_jobs_are_not_polled(self, mock_client_class):
        """Jobs already DONE/FAILED/CANCELED are excluded from the active queryset."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        self._make_job('DONE', request_id='req-done')
        self._make_job('FAILED', request_id='req-failed')
        self._make_job('CANCELED', request_id='req-canceled')

        monitor_batch_jobs()

        mock_client.get_request_status.assert_not_called()

    @patch('apps.satellite_processing.tasks.BatchClient')
    def test_unchanged_status_is_not_rewritten(self, mock_client_class):
        """No-op poll (status unchanged) shouldn't touch the job or trigger side effects."""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_request_status.return_value = 'ANALYSING'

        job = self._make_job('ANALYSING')

        monitor_batch_jobs()

        mock_client.execute_start.assert_not_called()
        job.refresh_from_db()
        self.assertEqual(job.status, 'ANALYSING')

    @patch('apps.satellite_processing.tasks.BatchClient')
    def test_one_job_error_does_not_abort_others(self, mock_client_class):
        """An exception while polling one job must not prevent polling the rest."""
        def status_for(request_id):
            if request_id == 'req-broken':
                raise Exception("boom")
            return 'ANALYSIS_DONE'

        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.get_request_status.side_effect = status_for

        self._make_job('ANALYSING', request_id='req-broken')
        healthy_job = self._make_job('ANALYSING', request_id='req-healthy')

        monitor_batch_jobs()

        healthy_job.refresh_from_db()
        self.assertEqual(healthy_job.status, 'PROCESSING')


class IngestBatchJobOutputsTest(TestCase):
    """Test the S3 -> SatelliteImage/VegetationIndex ingestion helper."""

    def setUp(self):
        self.region = Region.objects.create(
            name='Test Region',
            country='DRC',
            province='North Kivu',
            geometry='MULTIPOLYGON(((28.5 -1.5, 30.0 -1.5, 30.0 0.5, 28.5 0.5, 28.5 -1.5)))'
        )
        self.job = BatchJob.objects.create(
            request_id='req-ingest',
            region=self.region,
            status='DONE',
            bbox=[28.5, -1.5, 30.0, 0.5],
            time_range_start=timezone.make_aware(datetime(2024, 1, 1)),
            time_range_end=timezone.make_aware(datetime(2024, 1, 31)),
            s3_bucket='test-bucket'
        )
        self.stats = {'mean': 0.5, 'min': 0.1, 'max': 0.9, 'std': 0.1}

    def _output(self, tile_id='tile-1', date=None, key=None):
        date = date or datetime(2024, 1, 15)
        return {
            'key': key or f'ndvi/{tile_id}/{date.date().isoformat()}.tif',
            'tile_id': tile_id,
            'date': date,
        }

    @patch('apps.satellite_processing.tasks.SatelliteDataProcessor')
    def test_ingests_new_output_into_image_and_index(self, mock_processor_class):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor._calculate_raster_statistics.return_value = self.stats

        mock_client = MagicMock()
        mock_client.list_ndvi_outputs.return_value = [self._output()]

        count = _ingest_batch_job_outputs(self.job, mock_client)

        self.assertEqual(count, 1)
        self.assertEqual(SatelliteImage.objects.count(), 1)
        image = SatelliteImage.objects.get()
        self.assertTrue(image.is_processed)
        self.assertEqual(image.image_path, 's3://test-bucket/ndvi/tile-1/2024-01-15.tif')

        index = VegetationIndex.objects.get(satellite_image=image)
        self.assertEqual(index.index_type, 'NDVI')
        self.assertEqual(index.mean_value, 0.5)

    @patch('apps.satellite_processing.tasks.SatelliteDataProcessor')
    def test_skips_output_already_ingested(self, mock_processor_class):
        output = self._output()
        SatelliteImage.objects.create(
            region=self.job.region,
            acquisition_date=timezone.make_aware(output['date']),
            satellite_name='Sentinel-2',
            cloud_cover_percentage=0.0,
            resolution_meters=10.0,
            bands_available=['NDVI'],
            image_path=f"s3://{self.job.s3_bucket}/{output['key']}",
        )

        mock_client = MagicMock()
        mock_client.list_ndvi_outputs.return_value = [output]

        count = _ingest_batch_job_outputs(self.job, mock_client)

        self.assertEqual(count, 0)
        self.assertEqual(SatelliteImage.objects.count(), 1)
        mock_client.download_output.assert_not_called()

    @patch('apps.satellite_processing.tasks.SatelliteDataProcessor')
    def test_skips_output_outside_job_time_range(self, mock_processor_class):
        out_of_range = self._output(date=datetime(2023, 6, 1))

        mock_client = MagicMock()
        mock_client.list_ndvi_outputs.return_value = [out_of_range]

        count = _ingest_batch_job_outputs(self.job, mock_client)

        self.assertEqual(count, 0)
        self.assertEqual(SatelliteImage.objects.count(), 0)

    @patch('apps.satellite_processing.tasks.SatelliteDataProcessor')
    def test_per_output_failure_does_not_abort_remaining(self, mock_processor_class):
        mock_processor = MagicMock()
        mock_processor_class.return_value = mock_processor
        mock_processor._calculate_raster_statistics.return_value = self.stats

        mock_client = MagicMock()
        mock_client.list_ndvi_outputs.return_value = [
            self._output(tile_id='tile-bad'),
            self._output(tile_id='tile-good'),
        ]
        mock_client.download_output.side_effect = [Exception("download failed"), None]

        count = _ingest_batch_job_outputs(self.job, mock_client)

        self.assertEqual(count, 1)
        self.assertEqual(SatelliteImage.objects.count(), 1)

    @patch('apps.satellite_processing.tasks.SatelliteDataProcessor')
    def test_listing_failure_returns_zero(self, mock_processor_class):
        mock_client = MagicMock()
        mock_client.list_ndvi_outputs.side_effect = Exception("S3 unreachable")

        count = _ingest_batch_job_outputs(self.job, mock_client)

        self.assertEqual(count, 0)
        self.assertEqual(SatelliteImage.objects.count(), 0)
