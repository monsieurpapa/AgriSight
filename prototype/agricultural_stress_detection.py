#!/usr/bin/env python3
"""
AgriSight Project: Agricultural Stress Detection Prototype
This script demonstrates a prototype for detecting agricultural stress in the DRC
using satellite imagery and machine learning techniques.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import rasterio
from rasterio.plot import show
import geopandas as gpd
import ee
import datetime
import requests

# Initialize Earth Engine API (requires authentication in production)
# ee.Authenticate()
# ee.Initialize()
ee.Authenticate()
ee.Initialize(project="ee-dieudonneishara")

class AgriculturalStressDetector:
    """
    A class for detecting agricultural stress using satellite imagery and machine learning.
    """
    
    def __init__(self, region_of_interest=None):
        """
        Initialize the detector with a region of interest.
        
        Args:
            region_of_interest: GeoJSON or Earth Engine geometry representing the area of interest
        """
        self.roi = region_of_interest
        self.model = None
        self.baseline = None
        self.current = None
        
        # Define DRC conflict zones of interest
        if self.roi is None:
            # Default to North Kivu province if no ROI specified
            self.roi = ee.Geometry.Rectangle([28.5, -1.5, 30.0, 0.5])
            
        # Define vegetation indices to use
        self.indices = ['NDVI', 'EVI', 'NDWI', 'SAVI']
        
    def calculate_indices(self, image):
        """
        Calculate vegetation indices for a Sentinel-2 image.
        
        Args:
            image: Earth Engine image object
            
        Returns:
            Earth Engine image with added index bands
        """
        # Calculate NDVI (Normalized Difference Vegetation Index)
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
        # Calculate EVI (Enhanced Vegetation Index)
        evi = image.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4'),
                'BLUE': image.select('B2')
            }
        ).rename('EVI')
        
        # Calculate NDWI (Normalized Difference Water Index)
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        
        # Calculate SAVI (Soil-Adjusted Vegetation Index)
        savi = image.expression(
            '((NIR - RED) / (NIR + RED + 0.5)) * 1.5',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4')
            }
        ).rename('SAVI')
        
        # Add indices to the original image
        return image.addBands([ndvi, evi, ndwi, savi])
    
    def get_sentinel_collection(self, start_date, end_date):
        """
        Get a collection of Sentinel-2 images for the specified time period.
        
        Args:
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format
            
        Returns:
            Earth Engine image collection
        """
        # Get Sentinel-2 surface reflectance collection
        collection = ee.ImageCollection('COPERNICUS/S2_SR') \
            .filterDate(start_date, end_date) \
            .filterBounds(self.roi) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        
        # Map the index calculation function over the collection
        collection = collection.map(self.calculate_indices)
        
        return collection
    
    def create_monthly_composite(self, collection):
        """
        Create a monthly composite from a collection of images.
        
        Args:
            collection: Earth Engine image collection
            
        Returns:
            Earth Engine image
        """
        # Create a composite by taking the median value for each pixel
        composite = collection.median()
        
        return composite
    
    def detect_anomalies(self, baseline_period, current_period):
        """
        Detect anomalies by comparing current conditions to a baseline period.
        
        Args:
            baseline_period: Tuple of (start_date, end_date) for baseline period
            current_period: Tuple of (start_date, end_date) for current period
            
        Returns:
            Earth Engine image with anomaly scores
        """
        # Get baseline and current collections
        baseline_collection = self.get_sentinel_collection(*baseline_period)
        current_collection = self.get_sentinel_collection(*current_period)
        
        # Create monthly composites
        self.baseline = self.create_monthly_composite(baseline_collection)
        self.current = self.create_monthly_composite(current_collection)
        
        # Calculate difference for each vegetation index
        diff_image = ee.Image()
        
        for index in self.indices:
            # Calculate absolute difference
            diff = self.current.select(index).subtract(self.baseline.select(index)).abs()
            
            # Add to difference image
            diff_image = diff_image.addBands(diff.rename(f'{index}_diff'))
        
        return diff_image
    
    def classify_stress(self, diff_image, threshold=0.2):
        """
        Classify agricultural stress based on difference thresholds.
        
        Args:
            diff_image: Earth Engine image with difference bands
            threshold: Threshold value for stress classification
            
        Returns:
            Earth Engine image with stress classification
        """
        # Create a stress score based on the average of all index differences
        stress_score = ee.Image(0)
        
        for index in self.indices:
            stress_score = stress_score.add(diff_image.select(f'{index}_diff'))
        
        stress_score = stress_score.divide(len(self.indices)).rename('stress_score')
        
        # Classify stress levels
        stress_levels = stress_score.expression(
            'score > 0.3 ? 3 : (score > 0.2 ? 2 : (score > 0.1 ? 1 : 0))',
            {'score': stress_score}
        ).rename('stress_level')
        
        # Add stress classification to the image
        result = diff_image.addBands([stress_score, stress_levels])
        
        return result
    
    def visualize_stress(self, stress_image, output_path='stress_map_prod.png'):
        """
        Create a visualization of agricultural stress.
        
        Args:
            stress_image: Earth Engine image with stress classification
            output_path: Path to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        # Define visualization parameters
        vis_params = {
            'min': 0,
            'max': 3,
            'palette': ['green', 'yellow', 'orange', 'red']
        }
        
        # Create a map
        map_id = stress_image.select('stress_level').getMapId(vis_params)

        """
                # Create a simulated stress map
        plt.figure(figsize=(10, 10))
        
        # Create a random stress map for demonstration
        np.random.seed(42)  # For reproducibility
        stress_data = np.random.choice([0, 1, 2, 3], size=(100, 100), p=[0.5, 0.3, 0.15, 0.05])
        
        # Plot the stress map
        plt.imshow(stress_data, cmap='RdYlGn_r', interpolation='nearest')
        plt.colorbar(ticks=[0, 1, 2, 3], label='Stress Level')
        plt.title('Agricultural Stress Detection - DRC North Kivu Province')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        
        # Add a legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', label='No Stress'),
            Patch(facecolor='yellow', label='Low Stress'),
            Patch(facecolor='orange', label='Moderate Stress'),
            Patch(facecolor='red', label='High Stress')
        ]
        plt.legend(handles=legend_elements, loc='lower right')
        
        # Save the figure
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
        
        """
        
        # In a real implementation, we would download this image and save it
        # For this prototype, we'll simulate this with a placeholder visualization
        
        
        # Set thumbnail parameters
        region = stress_image.geometry().bounds().getInfo()['coordinates']
        # region = ee.Geometry.Polygon(region)
        thumbnail_params = {
            'dimensions': 1024,
            'region': region,
            'format': 'png',
            'min': vis_params['min'],
            'max': vis_params['max'],
            'palette': vis_params['palette'],
            'bands': ['stress_level']
        }

        # Get the thumbnail URL
        url = stress_image.getThumbURL(thumbnail_params)

        # Download and save the image
        response = requests.get(url)
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"Stress map saved to: {output_path}")
        else:
            raise Exception(f"Failed to download the image. Status code: {response.status_code}")


        
        return output_path
    
    def run_detection_pipeline(self, baseline_period, current_period, output_dir='./output'):
        """
        Run the complete agricultural stress detection pipeline.
        
        Args:
            baseline_period: Tuple of (start_date, end_date) for baseline period
            current_period: Tuple of (start_date, end_date) for current period
            output_dir: Directory to save outputs
            
        Returns:
            Dictionary with paths to output files
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Detect anomalies
        diff_image = self.detect_anomalies(baseline_period, current_period)
        
        # Classify stress
        stress_image = self.classify_stress(diff_image)
        
        # Visualize stress
        stress_map_path = os.path.join(output_dir, 'stress_map_prod.png')
        self.visualize_stress(stress_image, stress_map_path)
        
        # Generate summary statistics (simulated for prototype)
        summary = {
            'region': 'North Kivu, DRC',
            'baseline_period': f"{baseline_period[0]} to {baseline_period[1]}",
            'current_period': f"{current_period[0]} to {current_period[1]}",
            'stress_levels': {
                'no_stress': 50,    # Percentage of area with no stress
                'low_stress': 30,   # Percentage of area with low stress
                'moderate_stress': 15,  # Percentage of area with moderate stress
                'high_stress': 5    # Percentage of area with high stress
            },
            'affected_crops': ['Cassava', 'Maize', 'Plantains'],
            'potential_impact': 'Moderate risk to food security in conflict-affected areas'
        }
        
        # Save summary as JSON
        summary_path = os.path.join(output_dir, 'stress_summary.json')
        with open(summary_path, 'w') as f:
            import json
            json.dump(summary, f, indent=4)
        
        return {
            'stress_map': stress_map_path,
            'summary': summary_path
        }


def main():
    """
    Main function to demonstrate the agricultural stress detection prototype.
    """
    print("AgriSight Project: Agricultural Stress Detection Prototype")
    
    # Create detector
    detector = AgriculturalStressDetector()
    
    # Define time periods
    baseline_period = ('2024-01-01', '2024-03-31')  # Q1 2024 as baseline
    current_period = ('2024-04-01', '2024-06-30')   # Q2 2024 as current period
    
    # Run detection pipeline
    print(f"Running agricultural stress detection for North Kivu, DRC")
    print(f"Baseline period: {baseline_period[0]} to {baseline_period[1]}")
    print(f"Current period: {current_period[0]} to {current_period[1]}")
    
    # Create output directory
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    # For prototype demonstration, we'll create a simulated stress map
    print("Generating simulated agricultural stress map...")
    
    # Create a simulated stress map
    plt.figure(figsize=(10, 10))
    
    # Create a random stress map for demonstration
    np.random.seed(42)  # For reproducibility
    stress_data = np.random.choice([0, 1, 2, 3], size=(100, 100), p=[0.5, 0.3, 0.15, 0.05])
    
    # Plot the stress map
    plt.imshow(stress_data, cmap='RdYlGn_r', interpolation='nearest')
    plt.colorbar(ticks=[0, 1, 2, 3], label='Stress Level')
    plt.title('Agricultural Stress Detection - DRC North Kivu Province')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Add a legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='green', label='No Stress'),
        Patch(facecolor='yellow', label='Low Stress'),
        Patch(facecolor='orange', label='Moderate Stress'),
        Patch(facecolor='red', label='High Stress')
    ]
    plt.legend(handles=legend_elements, loc='lower right')
    
    # Save the figure
    stress_map_path = os.path.join(output_dir, 'stress_map_prod.png')
    plt.savefig(stress_map_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Stress map saved to: {stress_map_path}")
    
    # Generate summary statistics (simulated for prototype)
    """
        summary = {
        'region': 'North Kivu, DRC',
        'baseline_period': f"{baseline_period[0]} to {baseline_period[1]}",
        'current_period': f"{current_period[0]} to {current_period[1]}",
        'stress_levels': {
            'no_stress': 50,    # Percentage of area with no stress
            'low_stress': 30,   # Percentage of area with low stress
            'moderate_stress': 15,  # Percentage of area with moderate stress
            'high_stress': 5    # Percentage of area with high stress
        },
        'affected_crops': ['Cassava', 'Maize', 'Plantains'],
        'potential_impact': 'Moderate risk to food security in conflict-affected areas'
    }
    
    # Save summary as JSON
    summary_path = os.path.join(output_dir, 'stress_summary.json')
    with open(summary_path, 'w') as f:
        import json
        json.dump(summary, f, indent=4)
    
    print(f"Summary saved to: {summary_path}")
    """
    print("Agricultural stress detection prototype completed successfully.")


if __name__ == "__main__":
    main()
