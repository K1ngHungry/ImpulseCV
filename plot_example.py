#!/usr/bin/env python3
"""
Example script showing how to use the plotting functionality.
"""

import subprocess
import sys
import os

def run_plotting_examples():
    """Run various plotting examples."""
    
    print("=== ImpulseCV Plotting Examples ===\n")
    
    # Check if data files exist
    data_files = ['data.csv', 'data1.csv']
    available_files = [f for f in data_files if os.path.exists(f)]
    
    if not available_files:
        print("No CSV data files found. Please run main.py first to generate tracking data.")
        return
    
    print(f"Found data files: {available_files}\n")
    
    # Example 1: Basic trajectory plot
    print("1. Basic trajectory plot...")
    try:
        subprocess.run([sys.executable, 'plot_data.py', available_files[0]], check=True)
    except subprocess.CalledProcessError:
        print("Error running basic plot")
    
    # Example 2: With velocity vectors
    print("\n2. Trajectory with velocity vectors...")
    try:
        subprocess.run([sys.executable, 'plot_data.py', available_files[0], '--velocity'], check=True)
    except subprocess.CalledProcessError:
        print("Error running velocity plot")
    
    # Example 3: Track analysis
    print("\n3. Tracking quality analysis...")
    try:
        subprocess.run([sys.executable, 'plot_data.py', available_files[0], '--track-analysis'], check=True)
    except subprocess.CalledProcessError:
        print("Error running track analysis")
    
    # Example 4: Save plots to files
    print("\n4. Saving plots to files...")
    try:
        base_name = os.path.splitext(available_files[0])[0]
        subprocess.run([sys.executable, 'plot_data.py', available_files[0], 
                       '--velocity', '--track-analysis', 
                       '--save', f'{base_name}_plots', '--no-show'], check=True)
        print(f"Plots saved with prefix: {base_name}_plots")
    except subprocess.CalledProcessError:
        print("Error saving plots")
    
    print("\nPlotting examples complete!")

if __name__ == "__main__":
    run_plotting_examples()
