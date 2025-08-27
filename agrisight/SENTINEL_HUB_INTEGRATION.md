# Sentinel Hub Integration for AgriSight Platform

## Overview

This document describes the integration of Sentinel Hub Processing API into the AgriSight platform, enhancing its satellite data processing and analytics capabilities for agricultural monitoring in DRC conflict-affected areas.

## What is Sentinel Hub?

Sentinel Hub is a cloud-based platform that provides access to satellite imagery from various missions, including Sentinel-2, through standardized APIs. It offers:

- **On-demand processing** of satellite imagery
- **Custom evalscripts** for vegetation indices calculation
- **Cloud masking** and atmospheric correction
- **Multi-temporal analysis** capabilities
- **High-resolution data** (10m for Sentinel-2)

## Integration Benefits for AgriSight

### 1. Real-time Data Access
- Direct access to latest Sentinel-2 imagery without manual downloads
- Automated data ingestion through API calls
- Reduced latency from satellite acquisition to analysis

### 2. Advanced Processing Capabilities
- Custom evalscripts for vegetation indices (NDVI, EVI, NDWI, SAVI)
- Cloud masking for improved data quality
- Atmospheric correction for accurate reflectance values
- Multi-resolution processing options

### 3. Scalable Architecture
- API-based processing reduces local computational requirements
- Parallel processing of multiple regions
- Efficient handling of large-scale monitoring operations

### 4. Enhanced Analytics
- More accurate vegetation index calculations
- Better anomaly detection through statistical analysis
- Historical baseline comparisons
- Improved agricultural stress identification

## Technical Implementation

### Core Components

#### 1. SentinelHubClient (`apps/sentinel_hub/client.py`)
Main client class for interacting with Sentinel Hub Processing API:

```python
from apps.sentinel_hub.client import SentinelHubClient

client = SentinelHubClient()
response = client.get_vegetation_index(
    bbox=[29.0, -1.8, 29.5, -1.3],  # Goma region, DRC
    time_range=("2023-10-01T00:00:00Z", "2023-10-31T23:59:59Z"),
    index_type='ndvi'
)
```

**Key Features:**
- OAuth2 authentication with automatic token refresh
- Evalscript generation for all vegetation indices
- Error handling and retry logic
- Support for custom processing parameters

#### 2. Utility Functions (`apps/sentinel_hub/utils.py`)
Helper functions for data processing and validation:

```python
from apps.sentinel_hub.utils import geometry_to_bbox, validate_bbox

# Convert Django geometry to bbox
bbox = geometry_to_bbox(region.geometry)

# Validate coordinates
if validate_bbox(bbox):
    # Process the region
    pass
```

**Key Functions:**
- `geometry_to_bbox()`: Convert Django GEOSGeometry to bbox coordinates
- `validate_bbox()`: Validate bounding box coordinates
- `extract_statistics_from_tiff()`: Extract statistics from processed imagery
- `is_valid_vegetation_index_value()`: Validate vegetation index values

#### 3. Enhanced Celery Tasks (`celery_worker/tasks_sentinel_hub.py`)
Asynchronous processing tasks using Sentinel Hub API:

```python
# Ingest satellite data for a region
ingest_sentinel_data_enhanced.delay(region_id, start_date, end_date)

# Process satellite image with vegetation indices
process_satellite_image_enhanced.delay(image_id)

# Batch process multiple time periods
batch_process_region.delay(region_id, days_back=30)
```

**Enhanced Features:**
- Real API calls instead of mock data
- Statistical anomaly detection
- Historical baseline comparisons
- Batch processing capabilities

### Vegetation Indices Implementation

#### NDVI (Normalized Difference Vegetation Index)
```javascript
// Evalscript for NDVI calculation
function evaluatePixel(sample) {
    let ndvi = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
    return [ndvi];
}
```
- **Range:** -1 to 1
- **Use case:** General vegetation health assessment
- **Interpretation:** Higher values indicate healthier vegetation

#### EVI (Enhanced Vegetation Index)
```javascript
// Evalscript for EVI calculation
function evaluatePixel(sample) {
    let evi = 2.5 * ((sample.B08 - sample.B04) / (sample.B08 + 6 * sample.B04 - 7.5 * sample.B02 + 1));
    return [evi];
}
```
- **Range:** -1 to 1
- **Use case:** Improved vegetation monitoring in high biomass areas
- **Advantage:** Less sensitive to atmospheric conditions

#### NDWI (Normalized Difference Water Index)
```javascript
// Evalscript for NDWI calculation
function evaluatePixel(sample) {
    let ndwi = (sample.B03 - sample.B08) / (sample.B03 + sample.B08);
    return [ndwi];
}
```
- **Range:** -1 to 1
- **Use case:** Water stress detection and irrigation monitoring
- **Interpretation:** Higher values indicate more water content

#### SAVI (Soil Adjusted Vegetation Index)
```javascript
// Evalscript for SAVI calculation
function evaluatePixel(sample) {
    let L = 0.5;
    let savi = (sample.B08 - sample.B04) * (1 + L) / (sample.B08 + sample.B04 + L);
    return [savi];
}
```
- **Range:** -1 to 1
- **Use case:** Vegetation monitoring in areas with exposed soil
- **Advantage:** Reduces soil brightness influence

## Configuration

### Environment Variables
Add the following to your `.env` file:

```bash
# Sentinel Hub Configuration
SENTINEL_HUB_CLIENT_ID=your_client_id_here
SENTINEL_HUB_CLIENT_SECRET=your_client_secret_here
SENTINEL_HUB_BASE_URL=https://sh.dataspace.copernicus.eu/api/v1
SENTINEL_HUB_OAUTH_URL=https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token
```

### Django Settings
The integration is automatically configured in `settings.py`:

```python
# Sentinel Hub Configuration
SENTINEL_HUB_CLIENT_ID = config('SENTINEL_HUB_CLIENT_ID', default=None)
SENTINEL_HUB_CLIENT_SECRET = config('SENTINEL_HUB_CLIENT_SECRET', default=None)
```

### Dependencies
Additional Python packages required:

```
sentinelhub==3.9.1
oauthlib==3.2.2
requests-oauthlib==1.3.1
rasterio==1.3.9
```

## Usage Examples

### 1. Basic Vegetation Index Calculation

```python
from apps.sentinel_hub.client import SentinelHubClient
from datetime import datetime, timedelta

client = SentinelHubClient()

# Define area of interest (Goma region, DRC)
bbox = [29.0, -1.8, 29.5, -1.3]

# Define time range (last 30 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
time_range = (
    start_date.strftime("%Y-%m-%dT00:00:00Z"),
    end_date.strftime("%Y-%m-%dT23:59:59Z")
)

# Get NDVI data
ndvi_response = client.get_vegetation_index(
    bbox=bbox,
    time_range=time_range,
    index_type='ndvi',
    width=512,
    height=512,
    max_cloud_coverage=20.0
)

# Save to file
with open('ndvi_goma.tif', 'wb') as f:
    f.write(ndvi_response.content)
```

### 2. Batch Processing Multiple Regions

```python
from celery import group
from apps.sentinel_hub.tasks_sentinel_hub import batch_process_region

# Process multiple regions in parallel
regions = ['region_1_id', 'region_2_id', 'region_3_id']
job = group(batch_process_region.s(region_id, days_back=30) for region_id in regions)
result = job.apply_async()
```

### 3. Anomaly Detection Workflow

```python
from apps.sentinel_hub.tasks_sentinel_hub import (
    ingest_sentinel_data_enhanced,
    process_satellite_image_enhanced
)

# 1. Ingest new satellite data
ingest_task = ingest_sentinel_data_enhanced.delay(
    region_id='drc_region_1',
    start_date='2023-10-01T00:00:00Z',
    end_date='2023-10-31T23:59:59Z'
)

# 2. Processing will be automatically triggered
# 3. Anomalies will be detected and stored in AgriculturalStressEvent model
```

## AgriSight-Specific Use Cases

### 1. Conflict Zone Monitoring
- **Objective:** Monitor agricultural areas in DRC conflict zones
- **Implementation:** Regular NDVI monitoring to detect crop abandonment
- **Threshold:** NDVI < 0.3 indicates potential agricultural stress
- **Alert System:** Automatic alerts for humanitarian organizations

### 2. Food Security Assessment
- **Objective:** Assess crop health for food security planning
- **Implementation:** Multi-index analysis (NDVI + EVI + SAVI)
- **Baseline Comparison:** Compare current values with historical averages
- **Risk Classification:** Low/Medium/High risk based on vegetation indices

### 3. Water Stress Detection
- **Objective:** Identify areas experiencing water stress
- **Implementation:** NDWI monitoring combined with precipitation data
- **Early Warning:** Detect water stress before visible crop damage
- **Intervention Planning:** Guide irrigation and water resource allocation

### 4. Land Use Change Detection
- **Objective:** Track changes in agricultural land use
- **Implementation:** Time series analysis of vegetation indices
- **Change Detection:** Statistical analysis to identify significant changes
- **Reporting:** Automated reports for stakeholders

## Performance Considerations

### API Rate Limits
- Sentinel Hub has processing unit (PU) limits
- Monitor usage through dashboard
- Implement request queuing for high-volume processing

### Data Storage
- Processed imagery can be large (MB to GB per request)
- Implement cleanup routines for temporary files
- Consider cloud storage for long-term archival

### Processing Optimization
- Use appropriate resolution for analysis needs
- Implement caching for frequently accessed areas
- Batch similar requests to reduce API calls

## Error Handling

### Common Issues and Solutions

#### 1. Authentication Errors
```python
# Check credentials configuration
if not client.client_id or not client.client_secret:
    raise ValueError("Sentinel Hub credentials not configured")
```

#### 2. No Data Available
```python
# Handle cases where no imagery is available
try:
    response = client.get_vegetation_index(...)
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400:
        # No data available for the specified parameters
        logger.warning("No satellite data available for the specified time range")
```

#### 3. Cloud Coverage Issues
```python
# Adjust cloud coverage threshold
response = client.get_vegetation_index(
    bbox=bbox,
    time_range=time_range,
    index_type='ndvi',
    max_cloud_coverage=50.0  # Increase threshold if needed
)
```

## Testing

### Unit Tests
Run the comprehensive test suite:

```bash
cd /home/ubuntu/agrisight/backend
python3 test_sentinel_hub_standalone.py
```

### Integration Tests
Test with real API credentials:

```bash
# Set real credentials in .env file
export SENTINEL_HUB_CLIENT_ID="your_real_client_id"
export SENTINEL_HUB_CLIENT_SECRET="your_real_client_secret"

# Run integration tests
python3 manage.py test apps.sentinel_hub.tests
```

## Monitoring and Logging

### Logging Configuration
Sentinel Hub operations are logged with appropriate levels:

```python
import logging
logger = logging.getLogger('apps.sentinel_hub')

# Log levels:
# DEBUG: Detailed API request/response information
# INFO: Successful operations and processing status
# WARNING: Recoverable errors and fallback operations
# ERROR: Failed operations requiring attention
```

### Monitoring Metrics
Track key performance indicators:

- API request success rate
- Processing time per region
- Data quality metrics (cloud coverage, etc.)
- Anomaly detection accuracy
- System resource usage

## Future Enhancements

### 1. Additional Satellite Data Sources
- Integrate Landsat data for longer time series
- Add Sentinel-1 SAR data for all-weather monitoring
- Include Planet Labs high-resolution imagery

### 2. Advanced Analytics
- Machine learning models for crop type classification
- Yield prediction based on vegetation indices
- Climate change impact assessment

### 3. Real-time Processing
- Implement near real-time data ingestion
- Stream processing for immediate anomaly detection
- Push notifications for critical alerts

### 4. Enhanced Visualization
- Interactive maps with vegetation index overlays
- Time series charts for trend analysis
- Comparative analysis tools

## Conclusion

The Sentinel Hub integration significantly enhances AgriSight's capabilities for agricultural monitoring in DRC conflict zones. By providing real-time access to high-quality satellite imagery and advanced processing capabilities, the platform can now deliver more accurate, timely, and actionable insights for humanitarian organizations and agricultural stakeholders.

The implementation follows best practices for scalability, reliability, and maintainability, ensuring that the platform can grow to meet increasing demands for agricultural monitoring and food security assessment in challenging environments.

