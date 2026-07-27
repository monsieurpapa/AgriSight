"""
Tests for Sentinel Hub integration
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from django.test import TestCase
from django.contrib.gis.geos import Polygon
import requests

from .client import SentinelHubClient
from .batch_client import BatchClient
from .utils import (
    geometry_to_bbox, format_datetime_for_sentinel, get_time_range_for_period,
    validate_bbox, calculate_area_km2, is_valid_vegetation_index_value
)


class SentinelHubClientTest(TestCase):
    """Test cases for SentinelHubClient"""
    
    def setUp(self):
        self.client = SentinelHubClient()
        self.client.client_id = 'test_client_id'
        self.client.client_secret = 'test_client_secret'
    
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.base_url, "https://sh.dataspace.copernicus.eu/api/v1")
        self.assertEqual(self.client.oauth_url, "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token")
    
    @patch('requests.post')
    def test_get_access_token_success(self, mock_post):
        """Test successful access token retrieval"""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_token',
            'expires_in': 3600
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        token = self.client._get_access_token()
        
        self.assertEqual(token, 'test_token')
        self.assertEqual(self.client.access_token, 'test_token')
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_get_access_token_failure(self, mock_post):
        """Test access token retrieval failure"""
        mock_post.side_effect = requests.exceptions.RequestException("Auth failed")
        
        with self.assertRaises(requests.exceptions.RequestException):
            self.client._get_access_token()
    
    def test_generate_ndvi_evalscript(self):
        """Test NDVI evalscript generation"""
        evalscript = self.client.generate_ndvi_evalscript()
        
        self.assertIn('B04', evalscript)
        self.assertIn('B08', evalscript)
        self.assertIn('FLOAT32', evalscript)
        self.assertIn('ndvi', evalscript.lower())
    
    def test_generate_evi_evalscript(self):
        """Test EVI evalscript generation"""
        evalscript = self.client.generate_evi_evalscript()
        
        self.assertIn('B02', evalscript)
        self.assertIn('B04', evalscript)
        self.assertIn('B08', evalscript)
        self.assertIn('2.5', evalscript)
    
    def test_generate_ndwi_evalscript(self):
        """Test NDWI evalscript generation"""
        evalscript = self.client.generate_ndwi_evalscript()
        
        self.assertIn('B03', evalscript)
        self.assertIn('B08', evalscript)
        self.assertIn('FLOAT32', evalscript)
    
    def test_generate_savi_evalscript(self):
        """Test SAVI evalscript generation"""
        evalscript = self.client.generate_savi_evalscript(l_factor=0.5)
        
        self.assertIn('B04', evalscript)
        self.assertIn('B08', evalscript)
        self.assertIn('0.5', evalscript)
    
    def test_generate_true_color_evalscript(self):
        """Test true color evalscript generation"""
        evalscript = self.client.generate_true_color_evalscript()
        
        self.assertIn('B02', evalscript)
        self.assertIn('B03', evalscript)
        self.assertIn('B04', evalscript)
        self.assertIn('SCL', evalscript)
        self.assertIn('2.5', evalscript)


class SentinelHubUtilsTest(TestCase):
    """Test cases for Sentinel Hub utility functions"""
    
    def test_geometry_to_bbox(self):
        """Test geometry to bbox conversion"""
        # Create a simple polygon
        polygon = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        bbox = geometry_to_bbox(polygon)
        
        self.assertEqual(len(bbox), 4)
        self.assertEqual(bbox, [0.0, 0.0, 1.0, 1.0])
    
    def test_format_datetime_for_sentinel(self):
        """Test datetime formatting for Sentinel Hub API"""
        dt = datetime(2023, 10, 15, 12, 30, 45)
        formatted = format_datetime_for_sentinel(dt)
        
        self.assertEqual(formatted, "2023-10-15T12:30:45Z")
    
    def test_get_time_range_for_period(self):
        """Test time range generation"""
        end_date = datetime(2023, 10, 15, 12, 0, 0)
        start_str, end_str = get_time_range_for_period(end_date, days_back=7)
        
        self.assertTrue(start_str.endswith('Z'))
        self.assertTrue(end_str.endswith('Z'))
        self.assertEqual(end_str, "2023-10-15T12:00:00Z")
    
    def test_validate_bbox_valid(self):
        """Test bbox validation with valid coordinates"""
        valid_bbox = [-180, -90, 180, 90]
        self.assertTrue(validate_bbox(valid_bbox))
        
        valid_bbox2 = [13.8, 45.8, 14.6, 46.3]
        self.assertTrue(validate_bbox(valid_bbox2))
    
    def test_validate_bbox_invalid(self):
        """Test bbox validation with invalid coordinates"""
        # Wrong number of coordinates
        self.assertFalse(validate_bbox([1, 2, 3]))
        
        # Invalid longitude range
        self.assertFalse(validate_bbox([-200, -90, 180, 90]))
        
        # Invalid latitude range
        self.assertFalse(validate_bbox([-180, -100, 180, 90]))
        
        # Min >= Max
        self.assertFalse(validate_bbox([180, -90, -180, 90]))
    
    def test_calculate_area_km2(self):
        """Test area calculation"""
        # Small bbox (approximately 1 degree x 1 degree)
        bbox = [0, 0, 1, 1]
        area = calculate_area_km2(bbox)
        
        self.assertGreater(area, 0)
        self.assertIsInstance(area, float)
    
    def test_is_valid_vegetation_index_value(self):
        """Test vegetation index value validation"""
        # Valid NDVI values
        self.assertTrue(is_valid_vegetation_index_value(0.5, 'ndvi'))
        self.assertTrue(is_valid_vegetation_index_value(-0.2, 'ndvi'))
        self.assertTrue(is_valid_vegetation_index_value(0.9, 'ndvi'))
        
        # Invalid NDVI values
        self.assertFalse(is_valid_vegetation_index_value(1.5, 'ndvi'))
        self.assertFalse(is_valid_vegetation_index_value(-1.5, 'ndvi'))
        
        # Valid EVI values
        self.assertTrue(is_valid_vegetation_index_value(0.3, 'evi'))
        
        # Invalid index type
        self.assertFalse(is_valid_vegetation_index_value(0.5, 'invalid_index'))


class SentinelHubIntegrationTest(TestCase):
    """Integration tests for Sentinel Hub functionality"""
    
    def setUp(self):
        self.client = SentinelHubClient()
        # Mock credentials for testing
        self.client.client_id = 'test_client_id'
        self.client.client_secret = 'test_client_secret'
    
    @patch('apps.sentinel_hub.client.requests.post')
    @patch('apps.sentinel_hub.client.requests.request')
    def test_process_request_mock(self, mock_request, mock_post):
        """Test process request with mocked responses"""
        # Mock OAuth response
        mock_oauth_response = Mock()
        mock_oauth_response.json.return_value = {
            'access_token': 'test_token',
            'expires_in': 3600
        }
        mock_oauth_response.raise_for_status.return_value = None
        mock_post.return_value = mock_oauth_response
        
        # Mock process response
        mock_process_response = Mock()
        mock_process_response.content = b'fake_tiff_data'
        mock_process_response.raise_for_status.return_value = None
        mock_request.return_value = mock_process_response
        
        # Test parameters
        bbox = [13.8, 45.8, 14.6, 46.3]
        time_range = ("2023-10-01T00:00:00Z", "2023-10-31T23:59:59Z")
        evalscript = self.client.generate_ndvi_evalscript()
        
        # Make request
        response = self.client.process_request(
            bbox=bbox,
            time_range=time_range,
            evalscript=evalscript
        )
        
        self.assertEqual(response.content, b'fake_tiff_data')
        mock_post.assert_called_once()
        mock_request.assert_called_once()
    
    @patch('apps.sentinel_hub.client.SentinelHubClient.process_request')
    def test_get_vegetation_index_mock(self, mock_process_request):
        """Test vegetation index retrieval with mocked process request"""
        mock_response = Mock()
        mock_response.content = b'fake_ndvi_data'
        mock_process_request.return_value = mock_response
        
        bbox = [13.8, 45.8, 14.6, 46.3]
        time_range = ("2023-10-01T00:00:00Z", "2023-10-31T23:59:59Z")
        
        response = self.client.get_vegetation_index(
            bbox=bbox,
            time_range=time_range,
            index_type='ndvi'
        )
        
        self.assertEqual(response.content, b'fake_ndvi_data')
        mock_process_request.assert_called_once()
    
    def test_get_vegetation_index_invalid_type(self):
        """Test vegetation index retrieval with invalid index type"""
        bbox = [13.8, 45.8, 14.6, 46.3]
        time_range = ("2023-10-01T00:00:00Z", "2023-10-31T23:59:59Z")
        
        with self.assertRaises(ValueError):
            self.client.get_vegetation_index(
                bbox=bbox,
                time_range=time_range,
                index_type='invalid_index'
            )


class BatchClientTest(TestCase):
    """Test cases for BatchClient S3 output discovery and download"""

    def setUp(self):
        self.client = BatchClient()
        self.client.s3_bucket = 'test-bucket'
        self.client.s3_access_key = 'test-access-key'
        self.client.s3_secret_key = 'test-secret-key'
        self.client.s3_endpoint_url = 'https://s3.example.com'

    def _mock_s3(self, mock_get_s3_client, contents):
        mock_s3 = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{'Contents': contents}]
        mock_s3.get_paginator.return_value = mock_paginator
        mock_get_s3_client.return_value = mock_s3
        return mock_s3

    @patch('apps.sentinel_hub.batch_client.BatchClient.get_s3_client')
    def test_list_ndvi_outputs_parses_tile_and_date(self, mock_get_s3_client):
        """Keys matching the defaultTilePath template are parsed into tile_id/date"""
        self._mock_s3(mock_get_s3_client, [
            {'Key': 'ndvi/tile-42/2024-01-15.tif'},
        ])

        outputs = self.client.list_ndvi_outputs()

        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]['tile_id'], 'tile-42')
        self.assertEqual(outputs[0]['key'], 'ndvi/tile-42/2024-01-15.tif')
        self.assertEqual(outputs[0]['date'].year, 2024)
        self.assertEqual(outputs[0]['date'].month, 1)
        self.assertEqual(outputs[0]['date'].day, 15)

    @patch('apps.sentinel_hub.batch_client.BatchClient.get_s3_client')
    def test_list_ndvi_outputs_skips_unparseable_keys(self, mock_get_s3_client):
        """Keys that don't match the expected layout or have an unparseable date are skipped, not fatal"""
        self._mock_s3(mock_get_s3_client, [
            {'Key': 'ndvi/tile-1/not-a-date.tif'},
            {'Key': 'other-prefix/tile-2/2024-01-15.tif'},
            {'Key': 'ndvi/tile-3/2024-02-01.tif'},
        ])

        outputs = self.client.list_ndvi_outputs()

        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]['tile_id'], 'tile-3')

    @patch('apps.sentinel_hub.batch_client.BatchClient.get_s3_client')
    def test_list_ndvi_outputs_empty_bucket(self, mock_get_s3_client):
        """No Contents key in a page (empty prefix) returns an empty list, not an error"""
        mock_s3 = MagicMock()
        mock_paginator = MagicMock()
        mock_paginator.paginate.return_value = [{}]
        mock_s3.get_paginator.return_value = mock_paginator
        mock_get_s3_client.return_value = mock_s3

        outputs = self.client.list_ndvi_outputs()

        self.assertEqual(outputs, [])

    @patch('apps.sentinel_hub.batch_client.BatchClient.get_s3_client')
    def test_download_output_creates_dirs_and_downloads(self, mock_get_s3_client):
        """download_output makes the local directory tree before invoking the S3 download"""
        mock_s3 = MagicMock()
        mock_get_s3_client.return_value = mock_s3

        with tempfile.TemporaryDirectory() as tmp_dir:
            local_path = os.path.join(tmp_dir, 'nested', 'tile-1', 'out.tif')

            result = self.client.download_output('ndvi/tile-1/2024-01-15.tif', local_path)

            self.assertEqual(result, local_path)
            self.assertTrue(os.path.isdir(os.path.dirname(local_path)))
            mock_s3.download_file.assert_called_once_with(
                'test-bucket', 'ndvi/tile-1/2024-01-15.tif', local_path
            )


if __name__ == '__main__':
    unittest.main()

