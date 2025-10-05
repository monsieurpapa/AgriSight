#!/usr/bin/env python3
"""
Comprehensive test script for all new AgriSight features.
Run this script after starting Docker Compose to test all new functionality.
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"
HEALTH_URL = f"{BASE_URL}/health"
DETAILED_HEALTH_URL = f"{BASE_URL}/health/detailed"

# Test data
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password1": "testpass123!",
    "password2": "testpass123!"
}

TEST_ORGANIZATION = {
    "name": "Test Humanitarian Organization",
    "organization_type": "humanitarian",
    "contact_email": "contact@testorg.com",
    "description": "Test organization for AgriSight"
}

TEST_REGION = {
    "name": "Test Region North Kivu",
    "country": "DRC",
    "province": "North Kivu",
    "geometry": {
        "type": "MultiPolygon",
        "coordinates": [[[
            [28.5, -1.5],
            [30.0, -1.5],
            [30.0, 0.5],
            [28.5, 0.5],
            [28.5, -1.5]
        ]]]
    }
}

TEST_ML_MODEL = {
    "name": "Test Stress Detection Model",
    "model_type": "stress_detection",
    "algorithm": "random_forest",
    "version": "1.0.0",
    "description": "Test model for agricultural stress detection",
    "hyperparameters": {
        "n_estimators": 100,
        "max_depth": 10
    }
}


class AgriSightTester:
    """Comprehensive tester for AgriSight features."""
    
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.organization_id = None
        self.region_id = None
        self.model_id = None
        
    def log(self, message, level="INFO"):
        """Log test messages."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_health_checks(self):
        """Test health check endpoints."""
        self.log("Testing health check endpoints...")
        
        try:
            # Basic health check
            response = self.session.get(HEALTH_URL, timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                self.log(f"✓ Basic health check passed: {health_data}")
            else:
                self.log(f"✗ Basic health check failed: {response.status_code}", "ERROR")
                return False
            
            # Detailed health check
            response = self.session.get(DETAILED_HEALTH_URL, timeout=10)
            if response.status_code == 200:
                detailed_health = response.json()
                self.log(f"✓ Detailed health check passed: {detailed_health}")
                
                # Check service status
                services = detailed_health.get('services', {})
                for service, status in services.items():
                    if status == 'healthy':
                        self.log(f"✓ {service} service is healthy")
                    else:
                        self.log(f"✗ {service} service is unhealthy", "ERROR")
            else:
                self.log(f"✗ Detailed health check failed: {response.status_code}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"✗ Health check test failed: {str(e)}", "ERROR")
            return False
    
    def test_user_registration_and_login(self):
        """Test user registration and authentication."""
        self.log("Testing user registration and login...")
        
        try:
            # Register user
            response = self.session.post(f"{BASE_URL}/api/auth/registration/", json=TEST_USER)
            if response.status_code in [200, 201]:
                self.log("✓ User registration successful")
            else:
                self.log(f"✗ User registration failed: {response.status_code} - {response.text}", "ERROR")
                return False
            
            # Login user
            login_data = {
                "username": TEST_USER["username"],
                "password": TEST_USER["password1"]
            }
            response = self.session.post(f"{BASE_URL}/api/auth/login/", json=login_data)
            if response.status_code == 200:
                login_response = response.json()
                self.auth_token = login_response.get('access_token')
                if self.auth_token:
                    self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                    self.log("✓ User login successful")
                else:
                    self.log("✗ No access token received", "ERROR")
                    return False
            else:
                self.log(f"✗ User login failed: {response.status_code} - {response.text}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"✗ Authentication test failed: {str(e)}", "ERROR")
            return False
    
    def test_organization_management(self):
        """Test organization creation and management."""
        self.log("Testing organization management...")
        
        try:
            # Create organization
            response = self.session.post(f"{API_BASE}/organizations/", json=TEST_ORGANIZATION)
            if response.status_code in [200, 201]:
                org_data = response.json()
                self.organization_id = org_data.get('id')
                self.log(f"✓ Organization created: {org_data['name']}")
            else:
                self.log(f"✗ Organization creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
            
            # List organizations
            response = self.session.get(f"{API_BASE}/organizations/")
            if response.status_code == 200:
                organizations = response.json()
                self.log(f"✓ Retrieved {len(organizations)} organizations")
            else:
                self.log(f"✗ Failed to list organizations: {response.status_code}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"✗ Organization management test failed: {str(e)}", "ERROR")
            return False
    
    def test_region_management(self):
        """Test region creation and management."""
        self.log("Testing region management...")
        
        try:
            # Create region
            response = self.session.post(f"{API_BASE}/geospatial/regions/", json=TEST_REGION)
            if response.status_code in [200, 201]:
                region_data = response.json()
                self.region_id = region_data.get('id')
                self.log(f"✓ Region created: {region_data['name']}")
            else:
                self.log(f"✗ Region creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
            
            # List regions
            response = self.session.get(f"{API_BASE}/geospatial/regions/")
            if response.status_code == 200:
                regions = response.json()
                self.log(f"✓ Retrieved {len(regions)} regions")
            else:
                self.log(f"✗ Failed to list regions: {response.status_code}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"✗ Region management test failed: {str(e)}", "ERROR")
            return False
    
    def test_satellite_processing(self):
        """Test satellite data processing endpoints."""
        self.log("Testing satellite data processing...")
        
        try:
            # Get processing statistics
            response = self.session.get(f"{API_BASE}/satellite-processing/statistics/")
            if response.status_code == 200:
                stats = response.json()
                self.log(f"✓ Retrieved processing statistics: {stats}")
            else:
                self.log(f"✗ Failed to get processing statistics: {response.status_code}", "ERROR")
                return False
            
            # Test vegetation data endpoint
            if self.region_id:
                response = self.session.get(f"{API_BASE}/satellite-processing/vegetation/{self.region_id}/")
                if response.status_code == 200:
                    vegetation_data = response.json()
                    self.log(f"✓ Retrieved vegetation data for region")
                else:
                    self.log(f"✗ Failed to get vegetation data: {response.status_code}", "ERROR")
                    return False
            
            # Test trend analysis
            if self.region_id:
                trend_data = {
                    "region_id": self.region_id,
                    "months_back": 6
                }
                response = self.session.post(f"{API_BASE}/satellite-processing/trend-analysis/", json=trend_data)
                if response.status_code == 200:
                    trend_response = response.json()
                    self.log(f"✓ Started trend analysis: {trend_response}")
                else:
                    self.log(f"✗ Failed to start trend analysis: {response.status_code}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"✗ Satellite processing test failed: {str(e)}", "ERROR")
            return False
    
    def test_ml_models(self):
        """Test machine learning models functionality."""
        self.log("Testing ML models functionality...")
        
        try:
            # Create ML model
            response = self.session.post(f"{API_BASE}/ml-models/models/", json=TEST_ML_MODEL)
            if response.status_code in [200, 201]:
                model_data = response.json()
                self.model_id = model_data.get('id')
                self.log(f"✓ ML model created: {model_data['name']}")
            else:
                self.log(f"✗ ML model creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
            
            # List models
            response = self.session.get(f"{API_BASE}/ml-models/models/")
            if response.status_code == 200:
                models = response.json()
                self.log(f"✓ Retrieved {len(models)} ML models")
            else:
                self.log(f"✗ Failed to list ML models: {response.status_code}", "ERROR")
                return False
            
            # Start model training
            if self.model_id:
                training_data = {
                    "training_config": {
                        "validation_split": 0.2,
                        "random_state": 42
                    },
                    "data_sources": ["mock_training_data"]
                }
                response = self.session.post(f"{API_BASE}/ml-models/models/{self.model_id}/train/", json=training_data)
                if response.status_code == 200:
                    training_response = response.json()
                    self.log(f"✓ Started model training: {training_response}")
                else:
                    self.log(f"✗ Failed to start model training: {response.status_code}", "ERROR")
                    return False
            
            return True
            
        except Exception as e:
            self.log(f"✗ ML models test failed: {str(e)}", "ERROR")
            return False
    
    def test_security_features(self):
        """Test security features and middleware."""
        self.log("Testing security features...")
        
        try:
            # Test rate limiting (make multiple requests quickly)
            rate_limit_responses = []
            for i in range(5):
                response = self.session.get(f"{API_BASE}/geospatial/regions/")
                rate_limit_responses.append(response.status_code)
                time.sleep(0.1)  # Small delay
            
            self.log(f"✓ Rate limiting test completed: {rate_limit_responses}")
            
            # Test security headers
            response = self.session.get(f"{BASE_URL}/api/schema/")
            security_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection',
                'Content-Security-Policy'
            ]
            
            for header in security_headers:
                if header in response.headers:
                    self.log(f"✓ Security header present: {header}")
                else:
                    self.log(f"✗ Security header missing: {header}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"✗ Security features test failed: {str(e)}", "ERROR")
            return False
    
    def test_error_handling(self):
        """Test error handling and logging."""
        self.log("Testing error handling...")
        
        try:
            # Test 404 error
            response = self.session.get(f"{API_BASE}/nonexistent-endpoint/")
            if response.status_code == 404:
                self.log("✓ 404 error handling works correctly")
            else:
                self.log(f"✗ 404 error handling failed: {response.status_code}", "ERROR")
                return False
            
            # Test invalid data submission
            invalid_data = {"invalid": "data"}
            response = self.session.post(f"{API_BASE}/geospatial/regions/", json=invalid_data)
            if response.status_code in [400, 422]:
                self.log("✓ 400 error handling works correctly")
            else:
                self.log(f"✗ 400 error handling failed: {response.status_code}", "ERROR")
                return False
            
            return True
            
        except Exception as e:
            self.log(f"✗ Error handling test failed: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        self.log("Starting comprehensive AgriSight feature tests...")
        self.log("=" * 60)
        
        tests = [
            ("Health Checks", self.test_health_checks),
            ("User Authentication", self.test_user_registration_and_login),
            ("Organization Management", self.test_organization_management),
            ("Region Management", self.test_region_management),
            ("Satellite Processing", self.test_satellite_processing),
            ("ML Models", self.test_ml_models),
            ("Security Features", self.test_security_features),
            ("Error Handling", self.test_error_handling),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- Testing {test_name} ---")
            try:
                if test_func():
                    self.log(f"✓ {test_name} test PASSED")
                    passed_tests += 1
                else:
                    self.log(f"✗ {test_name} test FAILED", "ERROR")
            except Exception as e:
                self.log(f"✗ {test_name} test FAILED with exception: {str(e)}", "ERROR")
        
        self.log("\n" + "=" * 60)
        self.log(f"Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            self.log("🎉 ALL TESTS PASSED! All new features are working correctly.", "SUCCESS")
            return True
        else:
            self.log(f"❌ {total_tests - passed_tests} tests failed. Please check the logs above.", "ERROR")
            return False


def main():
    """Main test runner."""
    print("AgriSight New Features Test Suite")
    print("=" * 40)
    
    # Wait for services to be ready
    print("Waiting for services to start...")
    time.sleep(10)
    
    tester = AgriSightTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All new features are working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
