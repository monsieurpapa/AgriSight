#!/usr/bin/env python3
"""
AgriSight Project: Demonstration Script
This script demonstrates the key visualizations for the AgriSight presentation.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
import pandas as pd

# Create output directory
output_dir = './demo_visuals'
os.makedirs(output_dir, exist_ok=True)

def create_stress_map():
    """
    Create a visualization of agricultural stress in North Kivu province.
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Create a base map with geographical features (simplified for demo)
    plt.figure(figsize=(12, 10))
    
    # Create a stress map with realistic patterns
    # Higher values in northeast (conflict zone)
    y, x = np.indices((100, 100))
    conflict_pattern = (x / 100 + y / 100) / 2  # 0-1 gradient from SW to NE
    
    # Add some randomness but maintain the pattern
    noise = np.random.normal(0, 0.15, size=(100, 100))
    stress_data = conflict_pattern + noise
    
    # Classify into stress levels
    stress_levels = np.zeros_like(stress_data, dtype=int)
    stress_levels[stress_data < 0.3] = 0  # No stress
    stress_levels[(stress_data >= 0.3) & (stress_data < 0.5)] = 1  # Low stress
    stress_levels[(stress_data >= 0.5) & (stress_data < 0.7)] = 2  # Moderate stress
    stress_levels[stress_data >= 0.7] = 3  # High stress
    
    # Create custom colormap
    colors = ['green', 'yellow', 'orange', 'red']
    cmap = LinearSegmentedColormap.from_list('stress_cmap', colors, N=4)
    
    # Plot the stress map
    plt.imshow(stress_levels, cmap=cmap, interpolation='nearest')
    plt.colorbar(ticks=[0, 1, 2, 3], label='Stress Level')
    plt.title('Agricultural Stress Detection - North Kivu Province, DRC', fontsize=16)
    plt.xlabel('Longitude', fontsize=12)
    plt.ylabel('Latitude', fontsize=12)
    
    # Add a legend
    legend_elements = [
        mpatches.Patch(facecolor='green', label='No Stress'),
        mpatches.Patch(facecolor='yellow', label='Low Stress'),
        mpatches.Patch(facecolor='orange', label='Moderate Stress'),
        mpatches.Patch(facecolor='red', label='High Stress')
    ]
    plt.legend(handles=legend_elements, loc='lower right', fontsize=12)
    
    # Add conflict zone markers
    conflict_markers = [
        (75, 80, 'M23 Activity'),
        (85, 65, 'FDLR Presence'),
        (60, 90, 'ADF Conflict')
    ]
    
    for x, y, label in conflict_markers:
        plt.plot(x, y, 'kX', markersize=10)
        plt.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=10)
    
    # Add cities/reference points
    cities = [
        (30, 30, 'Goma'),
        (20, 70, 'Butembo'),
        (50, 20, 'Rutshuru')
    ]
    
    for x, y, label in cities:
        plt.plot(x, y, 'ko', markersize=6)
        plt.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=10)
    
    # Save the figure
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'agricultural_stress_map.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_change_detection_visualization():
    """
    Create a visualization of land use change detection over time.
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Create a figure with multiple subplots to show change over time
    fig = plt.figure(figsize=(15, 10))
    gs = GridSpec(2, 3, figure=fig)
    
    # Create dates for the time series
    dates = ['2023-01', '2023-06', '2023-12', '2024-06', '2024-12', '2025-03']
    
    # Base land use pattern
    land_use_base = np.zeros((100, 100), dtype=int)
    
    # Create some agricultural fields (value 1)
    for i in range(10):
        x = np.random.randint(10, 90)
        y = np.random.randint(10, 90)
        size = np.random.randint(5, 15)
        land_use_base[max(0, y-size):min(100, y+size), max(0, x-size):min(100, x+size)] = 1
    
    # Create land use maps with progressive changes
    land_use_maps = []
    
    # First map is the baseline
    land_use_maps.append(land_use_base.copy())
    
    # Create progressive changes (agricultural abandonment)
    for i in range(1, 6):
        prev_map = land_use_maps[i-1].copy()
        
        # Simulate conflict-induced abandonment (increasing with time)
        # More abandonment in the northeast (upper right)
        y, x = np.indices((100, 100))
        conflict_intensity = (x / 100 + y / 100) / 2  # 0-1 gradient from SW to NE
        
        # Probability of abandonment increases with conflict intensity and time
        abandon_prob = conflict_intensity * (i / 10)
        
        # Apply abandonment (change from 1 to 2, where 2 represents abandoned fields)
        random_mask = np.random.random(prev_map.shape) < abandon_prob
        agriculture_mask = prev_map == 1
        prev_map[(random_mask) & (agriculture_mask)] = 2
        
        land_use_maps.append(prev_map)
    
    # Plot the time series
    axes = []
    axes.append(fig.add_subplot(gs[0, 0]))
    axes.append(fig.add_subplot(gs[0, 1]))
    axes.append(fig.add_subplot(gs[0, 2]))
    axes.append(fig.add_subplot(gs[1, 0]))
    axes.append(fig.add_subplot(gs[1, 1]))
    axes.append(fig.add_subplot(gs[1, 2]))
    
    # Custom colormap for land use
    colors = ['lightgray', 'green', 'brown']
    cmap = LinearSegmentedColormap.from_list('land_use_cmap', colors, N=3)
    
    for i, ax in enumerate(axes):
        ax.imshow(land_use_maps[i], cmap=cmap, interpolation='nearest')
        ax.set_title(f'Land Use - {dates[i]}', fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
    
    # Add a legend
    legend_elements = [
        mpatches.Patch(facecolor='lightgray', label='Non-Agricultural'),
        mpatches.Patch(facecolor='green', label='Active Agriculture'),
        mpatches.Patch(facecolor='brown', label='Abandoned Agriculture')
    ]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize=12)
    
    # Add overall title
    fig.suptitle('Agricultural Land Use Change Detection in North Kivu (2023-2025)', fontsize=16)
    
    # Save the figure
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    output_path = os.path.join(output_dir, 'land_use_change_detection.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_conflict_agriculture_correlation():
    """
    Create a visualization showing the correlation between conflict events and agricultural stress.
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Create sample data
    months = pd.date_range(start='2023-01-01', end='2025-03-01', freq='MS')
    
    # Simulate conflict events with seasonal pattern and increasing trend
    conflict_events = 20 + 10 * np.sin(np.arange(len(months)) * (2 * np.pi / 12)) + np.arange(len(months)) * 0.5
    conflict_events = conflict_events + np.random.normal(0, 5, size=len(months))
    conflict_events = np.maximum(0, conflict_events).astype(int)
    
    # Simulate agricultural stress with lag (3 months) from conflict
    ag_stress = np.zeros(len(months))
    for i in range(len(months)):
        if i >= 3:
            # Agricultural stress is influenced by conflict events 3 months ago
            ag_stress[i] = 10 + 0.8 * conflict_events[i-3] + np.random.normal(0, 3)
        else:
            ag_stress[i] = 10 + np.random.normal(0, 3)
    
    # Create the figure
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # Plot conflict events
    ax1.set_xlabel('Date', fontsize=12)
    ax1.set_ylabel('Conflict Events', color='red', fontsize=12)
    ax1.plot(months, conflict_events, 'r-', label='Conflict Events')
    ax1.tick_params(axis='y', labelcolor='red')
    
    # Create second y-axis for agricultural stress
    ax2 = ax1.twinx()
    ax2.set_ylabel('Agricultural Stress Index', color='green', fontsize=12)
    ax2.plot(months, ag_stress, 'g-', label='Agricultural Stress')
    ax2.tick_params(axis='y', labelcolor='green')
    
    # Add vertical lines for major conflict escalations
    escalations = ['2023-05-01', '2023-11-01', '2024-08-01']
    for date in escalations:
        plt.axvline(x=pd.to_datetime(date), color='gray', linestyle='--', alpha=0.7)
        plt.text(pd.to_datetime(date), max(conflict_events) * 0.9, 'Conflict\nEscalation', 
                 rotation=90, verticalalignment='top', fontsize=10)
    
    # Add title and legend
    plt.title('Correlation Between Conflict Events and Agricultural Stress in North Kivu', fontsize=16)
    
    # Add combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # Add annotation about lag
    plt.annotate('3-month lag between\nconflict and agricultural impact', 
                 xy=(pd.to_datetime('2024-01-01'), 40),
                 xytext=(pd.to_datetime('2024-03-01'), 60),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8),
                 fontsize=10)
    
    # Save the figure
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'conflict_agriculture_correlation.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def create_implementation_timeline():
    """
    Create a visualization of the implementation timeline.
    """
    # Define the phases and their durations
    phases = ['Foundation', 'Core Functionality', 'Advanced Analytics', 'Operational System']
    durations = [3, 3, 3, 3]  # months
    
    # Define key activities for each phase
    activities = [
        ['Data pipelines', 'Preprocessing workflows', 'Basic monitoring'],
        ['Stress detection', 'Basic change detection', 'Web interface'],
        ['Land use tracking', 'ML model deployment', 'Conflict analysis'],
        ['Decision dashboard', 'Alerting system', 'Operational workflows']
    ]
    
    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Set up the y-axis
    ax.set_ylim(0, len(phases))
    ax.set_yticks(range(len(phases)))
    ax.set_yticklabels(phases)
    
    # Set up the x-axis (months)
    ax.set_xlim(0, sum(durations))
    ax.set_xticks(range(sum(durations) + 1))
    ax.set_xticklabels([f'Month {i}' for i in range(sum(durations) + 1)])
    plt.xticks(rotation=45)
    
    # Plot the phases as horizontal bars
    start = 0
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, (phase, duration) in enumerate(zip(phases, durations)):
        ax.barh(i, duration, left=start, height=0.5, color=colors[i], alpha=0.8)
        
        # Add text label in the middle of the bar
        ax.text(start + duration/2, i, phase, ha='center', va='center', color='white', fontweight='bold')
        
        # Add activities as smaller markers
        for j, activity in enumerate(activities[i]):
            activity_pos = start + (j + 1) * duration / (len(activities[i]) + 1)
            ax.scatter(activity_pos, i, color='white', s=100, zorder=5)
            ax.annotate(activity, (activity_pos, i), xytext=(0, 15), 
                        textcoords='offset points', ha='center', va='bottom',
                        bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.7))
        
        start += duration
    
    # Add milestones
    milestones = [
        (2, 'Initial Deployment'),
        (6, 'Stress Detection Live'),
        (9, 'Change Tracking Live'),
        (12, 'Full System Operational')
    ]
    
    for month, label in milestones:
        ax.axvline(x=month, color='black', linestyle='--', alpha=0.7)
        ax.annotate(label, (month, -0.2), xytext=(0, -20), 
                    textcoords='offset points', ha='center', va='top',
                    bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.7))
    
    # Add title
    plt.title('AgriSight Implementation Timeline', fontsize=16)
    
    # Add grid
    ax.grid(True, axis='x', linestyle='--', alpha=0.3)
    
    # Save the figure
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'implementation_timeline.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path

def main():
    """
    Generate all demonstration visuals for the AgriSight presentation.
    """
    print("Generating AgriSight demonstration visuals...")
    
    # Create the visualizations
    stress_map_path = create_stress_map()
    change_detection_path = create_change_detection_visualization()
    correlation_path = create_conflict_agriculture_correlation()
    timeline_path = create_implementation_timeline()
    
    print(f"Agricultural stress map saved to: {stress_map_path}")
    print(f"Land use change detection visualization saved to: {change_detection_path}")
    print(f"Conflict-agriculture correlation chart saved to: {correlation_path}")
    print(f"Implementation timeline saved to: {timeline_path}")
    
    print("All demonstration visuals generated successfully.")

if __name__ == "__main__":
    main()
