#!/usr/bin/env python3
"""
AgriSight Project: Agricultural Stress Detection Demo
This script runs the agricultural stress detection prototype and displays the results.
"""

import os
import json
import matplotlib.pyplot as plt
from agricultural_stress_detection import AgriculturalStressDetector

def main():
    """
    Main function to run the agricultural stress detection demo.
    """
    print("AgriSight Project: Agricultural Stress Detection Demo")
    print("====================================================")
    
    # Create output directory
    output_dir = './output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create detector
    detector = AgriculturalStressDetector()
    
    # Define time periods for North Kivu province
    baseline_period = ('2024-01-01', '2024-03-31')  # Q1 2024 as baseline
    current_period = ('2024-04-01', '2024-06-30')   # Q2 2024 as current period
    
    print(f"Running agricultural stress detection for North Kivu, DRC")
    print(f"Baseline period: {baseline_period[0]} to {baseline_period[1]}")
    print(f"Current period: {current_period[0]} to {current_period[1]}")
    
    # Run detection pipeline
    results = detector.run_detection_pipeline(baseline_period, current_period, output_dir)
    
    # Display results
    print("\nResults:")
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
    
    print("\nAgricultural stress detection demo completed successfully.")

if __name__ == "__main__":
    main()
