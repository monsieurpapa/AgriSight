"""
Sentinel Hub API Client for AgriSight Platform
Handles authentication and API requests to Sentinel Hub Processing API
"""

import requests
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SentinelHubClient:
    """
    Client for interacting with Sentinel Hub Processing API
    """
    
    def __init__(self):
        self.base_url = "https://sh.dataspace.copernicus.eu/api/v1"
        self.oauth_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.client_id = getattr(settings, 'SENTINEL_HUB_CLIENT_ID', None)
        self.client_secret = getattr(settings, 'SENTINEL_HUB_CLIENT_SECRET', None)
        self.access_token = None
        self.token_expires_at = None
        
        if not self.client_id or not self.client_secret:
            logger.warning("Sentinel Hub credentials not configured. Set SENTINEL_HUB_CLIENT_ID and SENTINEL_HUB_CLIENT_SECRET in settings.")
    
    def _get_access_token(self) -> str:
        """
        Get OAuth access token via sentinelhub SDK session (handles refresh automatically).
        """
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token

        if not self.client_id or not self.client_secret:
            raise ValueError("Sentinel Hub credentials not configured")

        try:
            from sentinelhub import SHConfig, SentinelHubSession
            config = SHConfig(
                sh_client_id=self.client_id,
                sh_client_secret=self.client_secret,
            )
            session = SentinelHubSession(config=config)
            token_data = session.token
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            logger.info("Obtained Sentinel Hub access token via SDK session")
            return self.access_token
        except ImportError:
            # sentinelhub SDK not available — fall back to direct OAuth
            pass
        except Exception as e:
            logger.error("sentinelhub SDK auth failed: %s — retrying with direct OAuth", e)

        # Direct OAuth fallback
        try:
            response = requests.post(self.oauth_url, data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            })
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            return self.access_token
        except requests.exceptions.RequestException as e:
            logger.error("Failed to obtain Sentinel Hub access token: %s", e)
            raise
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make authenticated request to Sentinel Hub API
        """
        token = self._get_access_token()
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {token}'
        kwargs['headers'] = headers
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        timeout = kwargs.pop('timeout', 20)

        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Sentinel Hub API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
    
    def generate_ndvi_evalscript(self) -> str:
        """
        Generate evalscript for NDVI calculation
        """
        return """
        //VERSION=3
        function setup() {
            return {
                input: ["B04", "B08"],
                output: {
                    bands: 1,
                    sampleType: "FLOAT32"
                }
            };
        }
        
        function evaluatePixel(sample) {
            let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
            return [ndvi];
        }
        """
    
    def generate_evi_evalscript(self) -> str:
        """
        Generate evalscript for EVI calculation
        """
        return """
        //VERSION=3
        function setup() {
            return {
                input: ["B02", "B04", "B08"],
                output: {
                    bands: 1,
                    sampleType: "FLOAT32"
                }
            };
        }
        
        function evaluatePixel(sample) {
            let evi = 2.5 * ((sample.B08 - sample.B04) / (sample.B08 + 6 * sample.B04 - 7.5 * sample.B02 + 1));
            return [evi];
        }
        """
    
    def generate_ndwi_evalscript(self) -> str:
        """
        Generate evalscript for NDWI calculation
        """
        return """
        //VERSION=3
        function setup() {
            return {
                input: ["B03", "B08"],
                output: {
                    bands: 1,
                    sampleType: "FLOAT32"
                }
            };
        }
        
        function evaluatePixel(sample) {
            let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
            return [ndwi];
        }
        """
    
    def generate_savi_evalscript(self, l_factor: float = 0.5) -> str:
        """
        Generate evalscript for SAVI calculation
        """
        return f"""
        //VERSION=3
        function setup() {{
            return {{
                input: ["B04", "B08"],
                output: {{
                    bands: 1,
                    sampleType: "FLOAT32"
                }}
            }};
        }}
        
        function evaluatePixel(sample) {{
            let L = {l_factor};
            let savi = (sample.B08 - sample.B04) * (1 + L) / (sample.B08 + sample.B04 + L);
            return [savi];
        }}
        """
    
    def generate_true_color_evalscript(self) -> str:
        """
        Generate evalscript for true color composite with cloud masking
        """
        return """
        //VERSION=3
        function setup() {
            return {
                input: ["B02", "B03", "B04", "SCL"],
                output: {
                    bands: 3,
                    sampleType: "AUTO"
                }
            };
        }
        
        function evaluatePixel(sample) {
            // Mask clouds, cloud shadows, and saturated pixels
            if ([8, 9, 10, 11].includes(sample.SCL)) {
                return [1, 0, 0]; // Red for masked pixels
            } else {
                return [2.5 * sample.B04, 2.5 * sample.B03, 2.5 * sample.B02];
            }
        }
        """
    
    def process_request(self, 
                       bbox: List[float], 
                       time_range: Tuple[str, str],
                       evalscript: str,
                       width: int = 512,
                       height: int = 512,
                       crs: str = "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
                       output_format: str = "image/tiff",
                       max_cloud_coverage: float = 20.0) -> requests.Response:
        """
        Make a processing request to Sentinel Hub
        
        Args:
            bbox: Bounding box coordinates [min_lon, min_lat, max_lon, max_lat]
            time_range: Tuple of (start_date, end_date) in ISO format
            evalscript: JavaScript evalscript for processing
            width: Output image width
            height: Output image height
            crs: Coordinate reference system
            output_format: Output format (image/tiff, image/png, etc.)
            max_cloud_coverage: Maximum cloud coverage percentage
        
        Returns:
            Response object containing the processed data
        """
        request_data = {
            "input": {
                "bounds": {
                    "properties": {"crs": crs},
                    "bbox": bbox
                },
                "data": [
                    {
                        "type": "sentinel-2-l2a",
                        "dataFilter": {
                            "timeRange": {
                                "from": time_range[0],
                                "to": time_range[1]
                            },
                            "maxCloudCoverage": max_cloud_coverage
                        }
                    }
                ]
            },
            "output": {
                "width": width,
                "height": height
            },
            "evalscript": evalscript
        }
        
        headers = {"Accept": output_format}
        
        return self._make_request(
            "POST", 
            "process", 
            json=request_data, 
            headers=headers
        )
    
    def get_vegetation_index(self, 
                           bbox: List[float], 
                           time_range: Tuple[str, str],
                           index_type: str,
                           **kwargs) -> requests.Response:
        """
        Get vegetation index data for a specific area and time range
        
        Args:
            bbox: Bounding box coordinates
            time_range: Time range tuple
            index_type: Type of vegetation index (ndvi, evi, ndwi, savi)
            **kwargs: Additional parameters for process_request
        
        Returns:
            Response containing the vegetation index data
        """
        evalscript_map = {
            'ndvi': self.generate_ndvi_evalscript,
            'evi': self.generate_evi_evalscript,
            'ndwi': self.generate_ndwi_evalscript,
            'savi': self.generate_savi_evalscript
        }
        
        if index_type.lower() not in evalscript_map:
            raise ValueError(f"Unsupported vegetation index type: {index_type}")
        
        evalscript = evalscript_map[index_type.lower()]()
        
        return self.process_request(
            bbox=bbox,
            time_range=time_range,
            evalscript=evalscript,
            output_format="image/tiff",
            **kwargs
        )
    
    def statistical_request(self,
                           bbox: List[float],
                           time_range: Tuple[str, str],
                           evalscript: str,
                           aggregation_interval: str = "P1D",
                           timeout: int = 20) -> dict:
        """
        Make a Statistical API request to get aggregated stats over a bbox/time range.

        Returns parsed JSON with mean NDVI per time bucket.
        """
        request_data = {
            "input": {
                "bounds": {
                    "bbox": bbox,
                    "properties": {"crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"},
                },
                "data": [{
                    "dataFilter": {
                        "timeRange": {"from": time_range[0], "to": time_range[1]},
                        "maxCloudCoverage": 30,
                    },
                    "type": "sentinel-2-l2a",
                }],
            },
            "aggregation": {
                "timeRange": {"from": time_range[0], "to": time_range[1]},
                "aggregationInterval": {"of": aggregation_interval},
                "evalscript": evalscript,
                "resx": 0.0001,
                "resy": 0.0001,
            },
        }
        response = self._make_request(
            "POST",
            "statistics",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=timeout,
        )
        return response.json()

    def get_true_color_image(self,
                           bbox: List[float],
                           time_range: Tuple[str, str],
                           **kwargs) -> requests.Response:
        """
        Get true color composite image
        
        Args:
            bbox: Bounding box coordinates
            time_range: Time range tuple
            **kwargs: Additional parameters for process_request
        
        Returns:
            Response containing the true color image
        """
        evalscript = self.generate_true_color_evalscript()
        
        return self.process_request(
            bbox=bbox,
            time_range=time_range,
            evalscript=evalscript,
            output_format="image/png",
            **kwargs
        )

