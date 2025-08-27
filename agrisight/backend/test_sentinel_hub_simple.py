#!/usr/bin/env python3
"""
Simple test script for Sentinel Hub integration without Django dependencies
"""

import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import requests

# Add the apps directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps'))

# Mock Django settings
class MockSettings:
    SENTINEL_HUB_CLIENT_ID = 'test_client_id'
    SENTINEL_HUB_CLIENT_SECRET = 'test_client_secret'

# Mock Django
class MockDjango:
    conf = MockSettings()

sys.modules['django'] = MockDjango()
sys.modules['django.conf'] = MockDjango()

# Import our modules
from sentinel_hub.client import SentinelHubClient
from sentinel_hub.utils import (
    format_datetime_for_sentinel, get_time_range_for_period,
    validate_bbox, is_valid_vegetation_index_value
)


def test_sentinel_hub_client():
    """Test SentinelHubClient functionality"""
    print("Testing SentinelHubClient...")
    
    client = SentinelHubClient()
    client.client_id = 'test_client_id'
    client.client_secret = 'test_client_secret'
    
    # Test evalscript generation
    ndvi_script = client.generate_ndvi_evalscript()
    assert 'B04' in ndvi_script and 'B08' in ndvi_script, "NDVI script should contain B04 and B08"
    print("✓ NDVI evalscript generation works")
    
    evi_script = client.generate_evi_evalscript()
    assert 'B02' in evi_script and 'B04' in evi_script and 'B08' in evi_script, "EVI script should contain B02, B04, and B08"
    print("✓ EVI evalscript generation works")
    
    ndwi_script = client.generate_ndwi_evalscript()
    assert 'B03' in ndwi_script and 'B08' in ndwi_script, "NDWI script should contain B03 and B08"
    print("✓ NDWI evalscript generation works")
    
    savi_script = client.generate_savi_evalscript(0.5)
    assert 'B04' in savi_script and 'B08' in savi_script and '0.5' in savi_script, "SAVI script should contain B04, B08, and L factor"
    print("✓ SAVI evalscript generation works")
    
    true_color_script = client.generate_true_color_evalscript()
    assert 'B02' in true_color_script and 'B03' in true_color_script and 'B04' in true_color_script, "True color script should contain RGB bands"
    print("✓ True color evalscript generation works")


def test_utility_functions():
    """Test utility functions"""
    print("\nTesting utility functions...")
    
    # Test datetime formatting
    dt = datetime(2023, 10, 15, 12, 30, 45)
    formatted = format_datetime_for_sentinel(dt)
    assert formatted == "2023-10-15T12:30:45Z", f"Expected '2023-10-15T12:30:45Z', got '{formatted}'"
    print("✓ Datetime formatting works")
    
    # Test time range generation
    end_date = datetime(2023, 10, 15, 12, 0, 0)
    start_str, end_str = get_time_range_for_period(end_date, days_back=7)
    assert start_str.endswith('Z') and end_str.endswith('Z'), "Time range should end with 'Z'"
    assert end_str == "2023-10-15T12:00:00Z", f"Expected '2023-10-15T12:00:00Z', got '{end_str}'"
    print("✓ Time range generation works")
    
    # Test bbox validation
    assert validate_bbox([13.8, 45.8, 14.6, 46.3]) == True, "Valid bbox should pass validation"
    assert validate_bbox([-200, -90, 180, 90]) == False, "Invalid longitude should fail validation"
    assert validate_bbox([1, 2, 3]) == False, "Wrong number of coordinates should fail validation"
    print("✓ Bbox validation works")
    
    # Test vegetation index validation
    assert is_valid_vegetation_index_value(0.5, 'ndvi') == True, "Valid NDVI value should pass"
    assert is_valid_vegetation_index_value(1.5, 'ndvi') == False, "Invalid NDVI value should fail"
    assert is_valid_vegetation_index_value(0.5, 'invalid_index') == False, "Invalid index type should fail"
    print("✓ Vegetation index validation works")


def test_mock_api_request():
    """Test API request with mocked responses"""
    print("\nTesting mocked API requests...")
    
    client = SentinelHubClient()
    client.client_id = 'test_client_id'
    client.client_secret = 'test_client_secret'
    
    # Mock the requests
    with patch('requests.post') as mock_post, patch('requests.request') as mock_request:
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
        evalscript = client.generate_ndvi_evalscript()
        
        # Make request
        response = client.process_request(
            bbox=bbox,
            time_range=time_range,
            evalscript=evalscript
        )
        
        assert response.content == b'fake_tiff_data', "Response content should match mock data"
        assert mock_post.called, "OAuth request should be called"
        assert mock_request.called, "Process request should be called"
        print("✓ Mocked API request works")


def test_vegetation_index_request():
    """Test vegetation index request"""
    print("\nTesting vegetation index requests...")
    
    client = SentinelHubClient()
    
    # Test invalid index type
    try:
        client.get_vegetation_index(
            bbox=[13.8, 45.8, 14.6, 46.3],
            time_range=("2023-10-01T00:00:00Z", "2023-10-31T23:59:59Z"),
            index_type='invalid_index'
        )
        assert False, "Should raise ValueError for invalid index type"
    except ValueError as e:
        assert "Unsupported vegetation index type" in str(e), "Should raise appropriate error message"
        print("✓ Invalid index type handling works")
    
    # Test valid index types
    valid_indices = ['ndvi', 'evi', 'ndwi', 'savi']
    for index_type in valid_indices:
        try:
            # This will fail without proper credentials, but should not raise ValueError
            with patch.object(client, 'process_request') as mock_process:
                mock_response = Mock()
                mock_response.content = b'fake_data'
                mock_process.return_value = mock_response
                
                response = client.get_vegetation_index(
                    bbox=[13.8, 45.8, 14.6, 46.3],
                    time_range=("2023-10-01T00:00:00Z", "2023-10-31T23:59:59Z"),
                    index_type=index_type
                )
                assert response.content == b'fake_data', f"Response should work for {index_type}"
        except ValueError:
            assert False, f"Should not raise ValueError for valid index type: {index_type}"
    
    print("✓ Vegetation index request handling works")


def main():
    """Run all tests"""
    print("Running Sentinel Hub Integration Tests")
    print("=" * 50)
    
    try:
        test_sentinel_hub_client()
        test_utility_functions()
        test_mock_api_request()
        test_vegetation_index_request()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("\nSentinel Hub integration is ready for use.")
        print("\nTo use with real data, you need to:")
        print("1. Register at https://dataspace.copernicus.eu/")
        print("2. Create OAuth client credentials")
        print("3. Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET in your .env file")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

