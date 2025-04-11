#!/usr/bin/env python3
"""
AgriSight Project: Agricultural Stress Detection Prototype (Mock Version)
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
import json

class MockAgriculturalStressDetector:
    """
    A mock class for demonstrating agricultural stress detection concepts.
    This version doesn't require Earth Engine authentication.
    """
    
    def __init__(self, region_name="North Kivu, DRC"):
        """
        Initialize the detector with a region name.
        
        Args:
            region_name: Name of the region of interest
        """
        self.region_name = region_name
        self.model = None
        self.baseline = None
        self.current = None
        
        # Define vegetation indices to use
        self.indices = ['NDVI', 'EVI', 'NDWI', 'SAVI']
        
        # For demonstration, create synthetic data
        np.random.seed(42)  # For reproducibility
        self.baseline_data = {
            'NDVI': np.random.normal(0.7, 0.15, size=(100, 100)),
            'EVI': np.random.normal(0.6, 0.12, size=(100, 100)),
            'NDWI': np.random.normal(-0.3, 0.1, size=(100, 100)),
            'SAVI': np.random.normal(0.65, 0.13, size=(100, 100))
        }
        
        # Clip values to realistic ranges
        for index in self.indices:
            self.baseline_data[index] = np.clip(self.baseline_data[index], 0, 1)
            
    def simulate_stress_patterns(self, stress_level=0.2, conflict_impact=0.3):
        """
        Simulate agricultural stress patterns based on parameters.
        
        Args:
            stress_level: Overall stress level (0-1)
            conflict_impact: Impact of conflict on stress (0-1)
            
        Returns:
            Dictionary with current data including simulated stress
        """
        # Create current data with some natural variation from baseline
        current_data = {}
        
        for index in self.indices:
            # Start with baseline
            base = self.baseline_data[index].copy()
            
            # Add random variation
            variation = np.random.normal(0, 0.05, size=base.shape)
            
            # Create stress pattern: higher in the northeast (simulating conflict zone)
            y, x = np.indices(base.shape)
            stress_pattern = (x / base.shape[1] + y / base.shape[0]) / 2  # 0-1 gradient from SW to NE
            
            # Apply stress (decrease vegetation indices in stress areas)
            # Different indices respond differently to stress
            if index in ['NDVI', 'EVI', 'SAVI']:
                # These decrease with stress
                stress_effect = -stress_level * stress_pattern * conflict_impact
            else:
                # NDWI might increase with stress (water stress can increase NDWI temporarily)
                stress_effect = stress_level * stress_pattern * conflict_impact * 0.5
                
            # Apply the stress effect
            current = base + variation + stress_effect
            
            # Clip to realistic values
            current_data[index] = np.clip(current, 0, 1)
            
        return current_data
    
    def detect_anomalies(self, stress_level=0.2, conflict_impact=0.3):
        """
        Detect anomalies by comparing current conditions to a baseline period.
        
        Args:
            stress_level: Overall stress level to simulate (0-1)
            conflict_impact: Impact of conflict on stress to simulate (0-1)
            
        Returns:
            Dictionary with difference data
        """
        # Simulate current data with stress patterns
        current_data = self.simulate_stress_patterns(stress_level, conflict_impact)
        self.current = current_data
        
        # Calculate differences
        diff_data = {}
        for index in self.indices:
            diff_data[f'{index}_diff'] = np.abs(current_data[index] - self.baseline_data[index])
            
        return diff_data
    
    def classify_stress(self, diff_data):
        """
        Classify agricultural stress based on difference thresholds.
        
        Args:
            diff_data: Dictionary with difference data
            
        Returns:
            Numpy array with stress classification
        """
        # Create a stress score based on the average of all index differences
        stress_score = np.zeros_like(diff_data[f'{self.indices[0]}_diff'])
        
        for index in self.indices:
            stress_score += diff_data[f'{index}_diff']
        
        stress_score /= len(self.indices)
        
        # Classify stress levels
        stress_levels = np.zeros_like(stress_score, dtype=int)
        stress_levels[stress_score > 0.1] = 1  # Low stress
        stress_levels[stress_score > 0.2] = 2  # Moderate stress
        stress_levels[stress_score > 0.3] = 3  # High stress
        
        return stress_levels
    
    def visualize_stress(self, stress_levels, output_path='stress_map.png'):
        """
        Create a visualization of agricultural stress.
        
        Args:
            stress_levels: Numpy array with stress classification
            output_path: Path to save the visualization
            
        Returns:
            Path to the saved visualization
        """
        # Create a figure
        plt.figure(figsize=(10, 10))
        
        # Plot the stress map
        plt.imshow(stress_levels, cmap='RdYlGn_r', interpolation='nearest')
        plt.colorbar(ticks=[0, 1, 2, 3], label='Stress Level')
        plt.title(f'Agricultural Stress Detection - {self.region_name}')
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
        
        # Add conflict zone markers (simulated)
        conflict_markers = [
            (75, 80, 'M23 Activity'),
            (85, 65, 'FDLR Presence'),
            (60, 90, 'ADF Conflict')
        ]
        
        for x, y, label in conflict_markers:
            plt.plot(x, y, 'kX', markersize=10)
            plt.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points')
        
        # Save the figure
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_summary_statistics(self, stress_levels):
        """
        Generate summary statistics from stress levels.
        
        Args:
            stress_levels: Numpy array with stress classification
            
        Returns:
            Dictionary with summary statistics
        """
        # Count pixels in each stress level
        unique, counts = np.unique(stress_levels, return_counts=True)
        total_pixels = stress_levels.size
        
        # Create percentage dictionary
        stress_percentages = {}
        for level, count in zip(unique, counts):
            if level == 0:
                stress_percentages['no_stress'] = round(count / total_pixels * 100)
            elif level == 1:
                stress_percentages['low_stress'] = round(count / total_pixels * 100)
            elif level == 2:
                stress_percentages['moderate_stress'] = round(count / total_pixels * 100)
            elif level == 3:
                stress_percentages['high_stress'] = round(count / total_pixels * 100)
                
        # Ensure all categories exist
        for category in ['no_stress', 'low_stress', 'moderate_stress', 'high_stress']:
            if category not in stress_percentages:
                stress_percentages[category] = 0
        
        return stress_percentages
    
    def run_detection_pipeline(self, baseline_period, current_period, output_dir='./output', 
                              stress_level=0.2, conflict_impact=0.3):
        """
        Run the complete agricultural stress detection pipeline.
        
        Args:
            baseline_period: Tuple of (start_date, end_date) for baseline period (for reporting only)
            current_period: Tuple of (start_date, end_date) for current period (for reporting only)
            output_dir: Directory to save outputs
            stress_level: Overall stress level to simulate (0-1)
            conflict_impact: Impact of conflict on stress to simulate (0-1)
            
        Returns:
            Dictionary with paths to output files
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Detect anomalies
        diff_data = self.detect_anomalies(stress_level, conflict_impact)
        
        # Classify stress
        stress_levels = self.classify_stress(diff_data)
        
        # Visualize stress
        stress_map_path = os.path.join(output_dir, 'stress_map.png')
        self.visualize_stress(stress_levels, stress_map_path)
        
        # Generate summary statistics
        stress_percentages = self.generate_summary_statistics(stress_levels)
        
        # Determine affected crops based on region
        if "North Kivu" in self.region_name:
            affected_crops = ['Cassava', 'Maize', 'Plantains', 'Beans']
        elif "South Kivu" in self.region_name:
            affected_crops = ['Cassava', 'Rice', 'Maize', 'Sweet Potatoes']
        elif "Ituri" in self.region_name:
            affected_crops = ['Cassava', 'Maize', 'Groundnuts', 'Rice']
        else:
            affected_crops = ['Cassava', 'Maize', 'Plantains']
            
        # Determine potential impact based on stress levels
        high_moderate = stress_percentages['high_stress'] + stress_percentages['moderate_stress']
        if high_moderate > 30:
            potential_impact = 'Severe risk to food security in conflict-affected areas'
        elif high_moderate > 15:
            potential_impact = 'Moderate risk to food security in conflict-affected areas'
        else:
            potential_impact = 'Low risk to food security, localized impacts in conflict hotspots'
        
        # Create summary
        summary = {
            'region': self.region_name,
            'baseline_period': f"{baseline_period[0]} to {baseline_period[1]}",
            'current_period': f"{current_period[0]} to {current_period[1]}",
            'stress_levels': stress_percentages,
            'affected_crops': affected_crops,
            'potential_impact': potential_impact,
            'conflict_correlation': 'High correlation between conflict intensity and agricultural stress',
            'recommendations': [
                'Prioritize food security interventions in northeastern areas',
                'Monitor cassava production closely as primary staple crop',
                'Establish early warning system for agricultural stress in conflict zones',
                'Implement drought-resistant crop varieties in high-stress areas'
            ]
        }
        
        # Save summary as JSON
        summary_path = os.path.join(output_dir, 'stress_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=4)
        
        return {
            'stress_map': stress_map_path,
            'summary': summary_path
        }


def main():
    """
    Main function to demonstrate the agricultural stress detection prototype.
    """
    print("AgriSight Project: Agricultural Stress Detection Prototype (Mock Version)")
    print("=====================================================================")
    
    # Create detector
    detector = MockAgriculturalStressDetector(region_name="North Kivu, DRC")
    
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
    
    # Run the pipeline with moderate stress and high conflict impact
    results = detector.run_detection_pipeline(
        baseline_period, 
        current_period, 
        output_dir,
        stress_level=0.25,  # Moderate stress
        conflict_impact=0.4  # High conflict impact
    )
    
    print(f"Stress map saved to: {results['stress_map']}")
    print(f"Summary saved to: {results['summary']}")
    
    # Load and display summary
    with open(results['summary'], 'r') as f:
        summary = json.load(f)
    
    print("\nSummary of Agricultural Stress Detection:")
    print(f"Region: {summary['region']}")
    print(f"Baseline period: {summary['baseline_period']}")
    print(f"Current period: {summary['current_period']}")
    
    print("\nStress Levels:")
    for level, percentage in summary['stress_levels'].items():
        print(f"  {level.replace('_', ' ').title()}: {percentage}%")
    
    print(f"\nAffected Crops: {', '.join(summary['affected_crops'])}")
    print(f"Potential Impact: {summary['potential_impact']}")
    print(f"Conflict Correlation: {summary['conflict_correlation']}")
    
    print("\nRecommendations:")
    for recommendation in summary['recommendations']:
        print(f"  - {recommendation}")
    
    print("\nAgricultural stress detection prototype completed successfully.")

if __name__ == "__main__":
    main()
