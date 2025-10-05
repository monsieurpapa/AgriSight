"""
Real satellite data processing implementation for AgriSight.
Replaces mock data with actual Sentinel Hub integration and vegetation index calculations.
"""

import os
import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.warp import calculate_default_transform, reproject, Resampling
import geopandas as gpd
from shapely.geometry import box
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional, Any
import requests
from django.conf import settings
from apps.sentinel_hub.client import SentinelHubClient
from apps.geospatial.models import Region, SatelliteImage, VegetationIndex
from apps.analytics.models import AgriculturalStressEvent

logger = logging.getLogger(__name__)


class SatelliteDataProcessor:
    """
    Real satellite data processor for vegetation index calculations and analysis.
    """
    
    def __init__(self):
        self.sentinel_client = SentinelHubClient()
        self.temp_dir = '/tmp/agrisight_processing'
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def process_region_satellite_data(self, region_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Process satellite data for a specific region and time period.
        
        Args:
            region_id: ID of the region to process
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            Dict with processing results and statistics
        """
        try:
            region = Region.objects.get(id=region_id)
            logger.info(f"Processing satellite data for region: {region.name}")
            
            # Get satellite data from Sentinel Hub
            satellite_data = self._fetch_sentinel_data(region, start_date, end_date)
            
            if not satellite_data:
                return {'error': 'No satellite data available for the specified period'}
            
            # Process each satellite image
            processing_results = []
            for image_data in satellite_data:
                result = self._process_single_image(image_data, region)
                processing_results.append(result)
            
            # Calculate region-wide statistics
            region_stats = self._calculate_region_statistics(processing_results, region)
            
            # Detect anomalies and create stress events
            stress_events = self._detect_agricultural_stress(processing_results, region)
            
            return {
                'region_id': region_id,
                'region_name': region.name,
                'processing_date': datetime.now().isoformat(),
                'images_processed': len(processing_results),
                'vegetation_indices_calculated': sum(len(r.get('indices', [])) for r in processing_results),
                'stress_events_detected': len(stress_events),
                'region_statistics': region_stats,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing satellite data for region {region_id}: {str(e)}")
            return {'error': str(e), 'success': False}
    
    def _fetch_sentinel_data(self, region: Region, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Fetch satellite data from Sentinel Hub for the specified region and time period.
        """
        try:
            # Convert region geometry to bounding box
            bbox = self._geometry_to_bbox(region.geometry)
            time_range = (start_date, end_date)
            
            # Get true color preview first
            preview_response = self.sentinel_client.get_true_color_image(
                bbox=bbox,
                time_range=time_range,
                width=1024,
                height=1024,
                max_cloud_coverage=20.0
            )
            
            if preview_response.status_code != 200:
                logger.warning(f"Failed to get preview image: {preview_response.status_code}")
                return []
            
            # Get vegetation indices
            vegetation_data = {}
            indices = ['ndvi', 'evi', 'ndwi', 'savi']
            
            for index_type in indices:
                try:
                    response = self.sentinel_client.get_vegetation_index(
                        bbox=bbox,
                        time_range=time_range,
                        index_type=index_type,
                        width=512,
                        height=512,
                        max_cloud_coverage=20.0
                    )
                    
                    if response.status_code == 200:
                        # Save the raster data
                        temp_file = f"{self.temp_dir}/{region.id}_{index_type}_{start_date}.tif"
                        with open(temp_file, 'wb') as f:
                            f.write(response.content)
                        vegetation_data[index_type] = temp_file
                    else:
                        logger.warning(f"Failed to get {index_type} data: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error fetching {index_type} data: {str(e)}")
                    continue
            
            if not vegetation_data:
                return []
            
            # Create satellite image record
            satellite_image = SatelliteImage.objects.create(
                region=region,
                acquisition_date=datetime.now(),
                satellite_name='Sentinel-2',
                cloud_cover_percentage=15.0,  # Estimated
                resolution_meters=10.0,
                bands_available=['B02', 'B03', 'B04', 'B08', 'B11', 'B12'],
                image_path=f"/data/satellite/{region.id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.tif",
                metadata={
                    'bbox': bbox,
                    'time_range': time_range,
                    'indices_available': list(vegetation_data.keys()),
                    'processing_timestamp': datetime.now().isoformat()
                }
            )
            
            return [{
                'satellite_image': satellite_image,
                'vegetation_files': vegetation_data,
                'bbox': bbox,
                'acquisition_date': satellite_image.acquisition_date
            }]
            
        except Exception as e:
            logger.error(f"Error fetching Sentinel data: {str(e)}")
            return []
    
    def _process_single_image(self, image_data: Dict[str, Any], region: Region) -> Dict[str, Any]:
        """
        Process a single satellite image and calculate vegetation indices.
        """
        satellite_image = image_data['satellite_image']
        vegetation_files = image_data['vegetation_files']
        
        results = {
            'satellite_image_id': str(satellite_image.id),
            'acquisition_date': satellite_image.acquisition_date,
            'indices': []
        }
        
        # Process each vegetation index
        for index_type, file_path in vegetation_files.items():
            try:
                # Calculate statistics from the raster
                stats = self._calculate_raster_statistics(file_path)
                
                # Create VegetationIndex record
                vegetation_index = VegetationIndex.objects.create(
                    satellite_image=satellite_image,
                    index_type=index_type.upper(),
                    mean_value=stats['mean'],
                    min_value=stats['min'],
                    max_value=stats['max'],
                    std_deviation=stats['std'],
                    raster_path=file_path
                )
                
                results['indices'].append({
                    'type': index_type.upper(),
                    'mean': stats['mean'],
                    'min': stats['min'],
                    'max': stats['max'],
                    'std': stats['std'],
                    'vegetation_index_id': str(vegetation_index.id)
                })
                
            except Exception as e:
                logger.error(f"Error processing {index_type}: {str(e)}")
                continue
        
        # Mark image as processed
        satellite_image.is_processed = True
        satellite_image.processing_notes = f"Processed with {len(results['indices'])} vegetation indices"
        satellite_image.save()
        
        return results
    
    def _calculate_raster_statistics(self, file_path: str) -> Dict[str, float]:
        """
        Calculate statistical measures from a raster file.
        """
        try:
            with rasterio.open(file_path) as src:
                data = src.read(1, masked=True)
                
                # Remove masked values
                valid_data = data.compressed()
                
                if len(valid_data) == 0:
                    return {'mean': 0.0, 'min': 0.0, 'max': 0.0, 'std': 0.0}
                
                return {
                    'mean': float(np.mean(valid_data)),
                    'min': float(np.min(valid_data)),
                    'max': float(np.max(valid_data)),
                    'std': float(np.std(valid_data))
                }
                
        except Exception as e:
            logger.error(f"Error calculating raster statistics for {file_path}: {str(e)}")
            return {'mean': 0.0, 'min': 0.0, 'max': 0.0, 'std': 0.0}
    
    def _calculate_region_statistics(self, processing_results: List[Dict[str, Any]], region: Region) -> Dict[str, Any]:
        """
        Calculate region-wide statistics from processing results.
        """
        if not processing_results:
            return {}
        
        # Aggregate vegetation index statistics
        aggregated_indices = {}
        
        for result in processing_results:
            for index_data in result.get('indices', []):
                index_type = index_data['type']
                if index_type not in aggregated_indices:
                    aggregated_indices[index_type] = []
                aggregated_indices[index_type].append(index_data['mean'])
        
        # Calculate regional averages
        regional_stats = {}
        for index_type, values in aggregated_indices.items():
            if values:
                regional_stats[index_type] = {
                    'mean': float(np.mean(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values)),
                    'std': float(np.std(values)),
                    'count': len(values)
                }
        
        return {
            'vegetation_indices': regional_stats,
            'total_area_hectares': region.area_hectares,
            'images_processed': len(processing_results),
            'processing_date': datetime.now().isoformat()
        }
    
    def _detect_agricultural_stress(self, processing_results: List[Dict[str, Any]], region: Region) -> List[str]:
        """
        Detect agricultural stress based on vegetation index analysis.
        """
        stress_events = []
        
        try:
            # Get historical data for comparison
            historical_data = self._get_historical_baseline(region)
            
            if not historical_data:
                logger.warning(f"No historical data available for region {region.name}")
                return stress_events
            
            # Analyze current data against historical baseline
            for result in processing_results:
                for index_data in result.get('indices', []):
                    index_type = index_data['type']
                    current_value = index_data['mean']
                    
                    if index_type in historical_data:
                        baseline = historical_data[index_type]
                        
                        # Calculate deviation from baseline
                        deviation = abs(current_value - baseline['mean'])
                        threshold = 2 * baseline['std']  # 2 standard deviations
                        
                        if deviation > threshold:
                            # Determine stress severity
                            severity = min(5, max(1, int(deviation / baseline['std'])))
                            
                            # Determine stress type based on index and deviation direction
                            stress_type = self._determine_stress_type(index_type, current_value, baseline['mean'])
                            
                            # Create stress event
                            stress_event = AgriculturalStressEvent.objects.create(
                                region=region,
                                detection_date=result['acquisition_date'].date(),
                                stress_type=stress_type,
                                severity=severity,
                                affected_area_hectares=region.area_hectares * 0.1,  # Assume 10% affected
                                description=f"{index_type} anomaly detected: {current_value:.3f} vs baseline {baseline['mean']:.3f} (deviation: {deviation:.3f})",
                                geometry=region.geometry
                            )
                            
                            stress_events.append(str(stress_event.id))
                            logger.info(f"Created stress event {stress_event.id} for region {region.name}")
            
        except Exception as e:
            logger.error(f"Error detecting agricultural stress: {str(e)}")
        
        return stress_events
    
    def _get_historical_baseline(self, region: Region) -> Dict[str, Dict[str, float]]:
        """
        Get historical baseline data for a region.
        """
        try:
            # Get vegetation indices from the last 12 months
            cutoff_date = datetime.now() - timedelta(days=365)
            
            recent_indices = VegetationIndex.objects.filter(
                satellite_image__region=region,
                satellite_image__acquisition_date__gte=cutoff_date,
                satellite_image__is_processed=True
            ).values('index_type', 'mean_value', 'std_deviation')
            
            baseline = {}
            for index in recent_indices:
                index_type = index['index_type']
                if index_type not in baseline:
                    baseline[index_type] = []
                baseline[index_type].append(index['mean_value'])
            
            # Calculate baseline statistics
            baseline_stats = {}
            for index_type, values in baseline.items():
                if len(values) >= 5:  # Need at least 5 observations
                    baseline_stats[index_type] = {
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)),
                        'count': len(values)
                    }
            
            return baseline_stats
            
        except Exception as e:
            logger.error(f"Error getting historical baseline: {str(e)}")
            return {}
    
    def _determine_stress_type(self, index_type: str, current_value: float, baseline_mean: float) -> str:
        """
        Determine the type of agricultural stress based on vegetation index analysis.
        """
        if index_type == 'NDVI':
            if current_value < baseline_mean * 0.8:
                return 'water'
            elif current_value < baseline_mean * 0.9:
                return 'nutrient'
            else:
                return 'other'
        elif index_type == 'NDWI':
            if current_value < baseline_mean * 0.7:
                return 'water'
            else:
                return 'other'
        elif index_type in ['EVI', 'SAVI']:
            if current_value < baseline_mean * 0.8:
                return 'disease'
            else:
                return 'other'
        else:
            return 'other'
    
    def _geometry_to_bbox(self, geometry) -> List[float]:
        """
        Convert Django geometry to bounding box format [min_lon, min_lat, max_lon, max_lat].
        """
        try:
            bounds = geometry.bounds
            return [bounds[0], bounds[1], bounds[2], bounds[3]]
        except Exception as e:
            logger.error(f"Error converting geometry to bbox: {str(e)}")
            return [28.5, -1.5, 30.0, 0.5]  # Default North Kivu bbox


class VegetationIndexCalculator:
    """
    Advanced vegetation index calculator with multiple algorithms.
    """
    
    @staticmethod
    def calculate_ndvi(nir_band: np.ndarray, red_band: np.ndarray) -> np.ndarray:
        """
        Calculate Normalized Difference Vegetation Index (NDVI).
        NDVI = (NIR - RED) / (NIR + RED)
        """
        # Avoid division by zero
        denominator = nir_band + red_band
        denominator[denominator == 0] = np.nan
        
        ndvi = (nir_band - red_band) / denominator
        return np.clip(ndvi, -1, 1)  # Clip to valid NDVI range
    
    @staticmethod
    def calculate_evi(nir_band: np.ndarray, red_band: np.ndarray, blue_band: np.ndarray) -> np.ndarray:
        """
        Calculate Enhanced Vegetation Index (EVI).
        EVI = 2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))
        """
        numerator = nir_band - red_band
        denominator = nir_band + 6 * red_band - 7.5 * blue_band + 1
        
        # Avoid division by zero
        denominator[denominator == 0] = np.nan
        
        evi = 2.5 * (numerator / denominator)
        return np.clip(evi, -1, 1)
    
    @staticmethod
    def calculate_ndwi(green_band: np.ndarray, nir_band: np.ndarray) -> np.ndarray:
        """
        Calculate Normalized Difference Water Index (NDWI).
        NDWI = (GREEN - NIR) / (GREEN + NIR)
        """
        numerator = green_band - nir_band
        denominator = green_band + nir_band
        
        # Avoid division by zero
        denominator[denominator == 0] = np.nan
        
        ndwi = numerator / denominator
        return np.clip(ndwi, -1, 1)
    
    @staticmethod
    def calculate_savi(nir_band: np.ndarray, red_band: np.ndarray, l_factor: float = 0.5) -> np.ndarray:
        """
        Calculate Soil-Adjusted Vegetation Index (SAVI).
        SAVI = ((NIR - RED) / (NIR + RED + L)) * (1 + L)
        """
        numerator = nir_band - red_band
        denominator = nir_band + red_band + l_factor
        
        # Avoid division by zero
        denominator[denominator == 0] = np.nan
        
        savi = (numerator / denominator) * (1 + l_factor)
        return np.clip(savi, -1, 1)
    
    @staticmethod
    def calculate_all_indices(bands: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        Calculate all vegetation indices from band data.
        
        Args:
            bands: Dictionary with band names as keys and arrays as values
            
        Returns:
            Dictionary with vegetation index names as keys and calculated arrays as values
        """
        indices = {}
        
        # NDVI
        if 'B08' in bands and 'B04' in bands:
            indices['NDVI'] = VegetationIndexCalculator.calculate_ndvi(bands['B08'], bands['B04'])
        
        # EVI
        if 'B08' in bands and 'B04' in bands and 'B02' in bands:
            indices['EVI'] = VegetationIndexCalculator.calculate_evi(bands['B08'], bands['B04'], bands['B02'])
        
        # NDWI
        if 'B03' in bands and 'B08' in bands:
            indices['NDWI'] = VegetationIndexCalculator.calculate_ndwi(bands['B03'], bands['B08'])
        
        # SAVI
        if 'B08' in bands and 'B04' in bands:
            indices['SAVI'] = VegetationIndexCalculator.calculate_savi(bands['B08'], bands['B04'])
        
        return indices
