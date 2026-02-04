"""
Utility functions for Sentinel Hub integration
"""

import os
import tempfile
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from django.contrib.gis.geos import Polygon
import rasterio
import numpy as np
import logging

logger = logging.getLogger(__name__)


def geometry_to_bbox(geometry) -> List[float]:
    """
    Convert Django GEOSGeometry to bounding box coordinates
    
    Args:
        geometry: Django GEOSGeometry object
    
    Returns:
        List of bbox coordinates [min_lon, min_lat, max_lon, max_lat]
    """
    if hasattr(geometry, 'extent'):
        extent = geometry.extent
        return [extent[0], extent[1], extent[2], extent[3]]  # [min_lon, min_lat, max_lon, max_lat]
    else:
        raise ValueError("Invalid geometry object")


def format_datetime_for_sentinel(dt: datetime) -> str:
    """
    Format datetime for Sentinel Hub API
    
    Args:
        dt: Python datetime object
    
    Returns:
        ISO formatted datetime string
    """
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def get_time_range_for_period(end_date: datetime, days_back: int = 30) -> Tuple[str, str]:
    """
    Get time range for a specific period
    
    Args:
        end_date: End date for the time range
        days_back: Number of days to go back from end_date
    
    Returns:
        Tuple of (start_date, end_date) in ISO format
    """
    start_date = end_date - timedelta(days=days_back)
    return (
        format_datetime_for_sentinel(start_date),
        format_datetime_for_sentinel(end_date)
    )


def save_response_to_file(response, file_path: str) -> str:
    """
    Save HTTP response content to file
    
    Args:
        response: HTTP response object
        file_path: Path where to save the file
    
    Returns:
        Path to the saved file
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'wb') as f:
        f.write(response.content)
    
    logger.info(f"Saved response to {file_path}")
    return file_path


def extract_statistics_from_tiff(file_path: str) -> dict:
    """
    Extract basic statistics from a GeoTIFF file
    
    Args:
        file_path: Path to the GeoTIFF file
    
    Returns:
        Dictionary containing statistics
    """
    try:
        with rasterio.open(file_path) as src:
            # Read the first band
            data = src.read(1)
            
            # Mask out nodata values
            if src.nodata is not None:
                data = np.ma.masked_equal(data, src.nodata)
            
            # Calculate statistics
            stats = {
                'min': float(np.min(data)) if not np.ma.is_masked(data) else None,
                'max': float(np.max(data)) if not np.ma.is_masked(data) else None,
                'mean': float(np.mean(data)) if not np.ma.is_masked(data) else None,
                'std': float(np.std(data)) if not np.ma.is_masked(data) else None,
                'count': int(np.count_nonzero(~np.ma.getmask(data))) if np.ma.is_masked(data) else int(data.size),
                'nodata_count': int(np.count_nonzero(np.ma.getmask(data))) if np.ma.is_masked(data) else 0
            }
            
            return stats
            
    except Exception as e:
        logger.error(f"Failed to extract statistics from {file_path}: {e}")
        return {}


def validate_bbox(bbox: List[float]) -> bool:
    """
    Validate bounding box coordinates
    
    Args:
        bbox: List of coordinates [min_lon, min_lat, max_lon, max_lat]
    
    Returns:
        True if valid, False otherwise
    """
    if len(bbox) != 4:
        return False
    
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Check coordinate ranges
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        return False
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        return False
    
    # Check that min < max
    if min_lon >= max_lon or min_lat >= max_lat:
        return False
    
    return True


def calculate_area_km2(bbox: List[float]) -> float:
    """
    Calculate approximate area of bounding box in square kilometers
    
    Args:
        bbox: List of coordinates [min_lon, min_lat, max_lon, max_lat]
    
    Returns:
        Area in square kilometers
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Create polygon from bbox
    polygon = Polygon.from_bbox(bbox)
    polygon.srid = 4326
    
    # Transform to appropriate projected CRS for area calculation
    # Using Web Mercator (EPSG:3857) for approximate calculation
    polygon_3857 = polygon.transform(3857, clone=True)
    
    # Area in square meters, convert to square kilometers
    area_km2 = polygon_3857.area / 1_000_000
    
    return area_km2


def get_optimal_resolution(area_km2: float) -> Tuple[int, int]:
    """
    Get optimal resolution based on area size
    
    Args:
        area_km2: Area in square kilometers
    
    Returns:
        Tuple of (width, height) in pixels
    """
    if area_km2 < 100:  # Small areas
        return (1024, 1024)
    elif area_km2 < 1000:  # Medium areas
        return (512, 512)
    else:  # Large areas
        return (256, 256)


def create_temp_file(suffix: str = '.tif') -> str:
    """
    Create a temporary file path
    
    Args:
        suffix: File extension
    
    Returns:
        Path to temporary file
    """
    temp_dir = tempfile.gettempdir()
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, dir=temp_dir)
    temp_file.close()
    return temp_file.name


def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary file
    
    Args:
        file_path: Path to file to delete
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.debug(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up temporary file {file_path}: {e}")


def is_valid_vegetation_index_value(value: float, index_type: str) -> bool:
    """
    Check if vegetation index value is within valid range
    
    Args:
        value: Index value to check
        index_type: Type of vegetation index
    
    Returns:
        True if valid, False otherwise
    """
    valid_ranges = {
        'ndvi': (-1.0, 1.0),
        'evi': (-1.0, 1.0),
        'ndwi': (-1.0, 1.0),
        'savi': (-1.0, 1.0)
    }
    
    if index_type.lower() not in valid_ranges:
        return False
    
    min_val, max_val = valid_ranges[index_type.lower()]
    return min_val <= value <= max_val
