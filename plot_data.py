#!/usr/bin/env python3
"""
Simple script to plot CSV tracking data from ImpulseCV.
Shows ball trajectory, position over time, and velocity analysis.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

def load_and_clean_data(csv_file):
    """Load CSV data and handle missing values."""
    print(f"Loading data from {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Sort by frame to ensure proper order
    df = df.sort_values('frame').reset_index(drop=True)
    
    print(f"Loaded {len(df)} data points")
    print(f"Frame range: {df['frame'].min()} to {df['frame'].max()}")
    print(f"Time range: {df['time_s'].min():.3f}s to {df['time_s'].max():.3f}s")
    
    return df

def calculate_velocity(df):
    """Calculate velocity between consecutive frames."""
    df = df.copy()
    
    # Calculate velocity in pixels per frame
    df['vx'] = df['cx'].diff()
    df['vy'] = df['cy'].diff()
    
    # Calculate velocity magnitude
    df['velocity'] = np.sqrt(df['vx']**2 + df['vy']**2)
    
    # Calculate velocity in pixels per second
    df['vx_ps'] = df['vx'] * 30  # Assuming 30 FPS
    df['vy_ps'] = df['vy'] * 30
    df['velocity_ps'] = df['velocity'] * 30
    
    return df

def plot_trajectory(df, title="Ball Trajectory"):
    """Plot the ball's trajectory in 2D space."""
    plt.figure(figsize=(12, 8))
    
    # Main trajectory plot
    plt.subplot(2, 2, 1)
    
    # Color by time progression
    scatter = plt.scatter(df['cx'], df['cy'], c=df['time_s'], cmap='viridis', 
                         s=30, alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # Add start and end markers
    if len(df) > 0:
        plt.scatter(df['cx'].iloc[0], df['cy'].iloc[0], c='green', s=100, 
                   marker='o', label='Start', edgecolors='black', linewidth=2)
        plt.scatter(df['cx'].iloc[-1], df['cy'].iloc[-1], c='red', s=100, 
                   marker='s', label='End', edgecolors='black', linewidth=2)
    
    plt.title(title)
    plt.xlabel('X Position (pixels)')
    plt.ylabel('Y Position (pixels)')
    plt.colorbar(scatter, label='Time (seconds)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')  # Equal aspect ratio
    
    # Position over time
    plt.subplot(2, 2, 2)
    plt.plot(df['time_s'], df['cx'], 'b-', label='X Position', linewidth=2)
    plt.plot(df['time_s'], df['cy'], 'r-', label='Y Position', linewidth=2)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Position (pixels)')
    plt.title('Position vs Time')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Velocity magnitude
    if 'velocity' in df.columns:
        plt.subplot(2, 2, 3)
        plt.plot(df['time_s'][1:], df['velocity'][1:], 'g-', linewidth=2)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Velocity (pixels/frame)')
        plt.title('Velocity Magnitude')
        plt.grid(True, alpha=0.3)
        
        # Add velocity statistics
        avg_vel = df['velocity'].mean()
        max_vel = df['velocity'].max()
        plt.axhline(y=avg_vel, color='orange', linestyle='--', alpha=0.7, 
                   label=f'Avg: {avg_vel:.1f} px/frame')
        plt.axhline(y=max_vel, color='red', linestyle='--', alpha=0.7, 
                   label=f'Max: {max_vel:.1f} px/frame')
        plt.legend()
    
    # Confidence over time
    plt.subplot(2, 2, 4)
    plt.plot(df['time_s'], df['conf'], 'purple', linewidth=2)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Detection Confidence')
    plt.title('Detection Confidence vs Time')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    
    # Add confidence statistics
    avg_conf = df['conf'].mean()
    min_conf = df['conf'].min()
    plt.axhline(y=avg_conf, color='orange', linestyle='--', alpha=0.7, 
               label=f'Avg: {avg_conf:.3f}')
    plt.axhline(y=min_conf, color='red', linestyle='--', alpha=0.7, 
               label=f'Min: {min_conf:.3f}')
    plt.legend()
    
    plt.tight_layout()
    return plt.gcf()

def plot_velocity_vectors(df, sample_rate=5):
    """Plot velocity vectors on the trajectory."""
    if 'vx' not in df.columns or 'vy' not in df.columns:
        print("Velocity data not available. Calculating...")
        df = calculate_velocity(df)
    
    plt.figure(figsize=(10, 8))
    
    # Plot trajectory
    plt.scatter(df['cx'], df['cy'], c=df['time_s'], cmap='viridis', 
               s=20, alpha=0.6, label='Trajectory')
    
    # Sample velocity vectors (every nth frame to avoid clutter)
    sample_df = df.iloc[::sample_rate]
    
    # Plot velocity vectors
    plt.quiver(sample_df['cx'], sample_df['cy'], 
               sample_df['vx'], sample_df['vy'], 
               sample_df['time_s'], cmap='plasma', 
               scale=100, alpha=0.8, width=0.003)
    
    plt.title('Ball Trajectory with Velocity Vectors')
    plt.xlabel('X Position (pixels)')
    plt.ylabel('Y Position (pixels)')
    plt.colorbar(label='Time (seconds)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    
    return plt.gcf()

def plot_track_analysis(df):
    """Analyze and plot tracking quality."""
    if 'track_id' not in df.columns:
        print("Track ID data not available")
        return None
    
    plt.figure(figsize=(12, 6))
    
    # Track ID over time
    plt.subplot(1, 2, 1)
    plt.plot(df['time_s'], df['track_id'], 'o-', markersize=4)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Track ID')
    plt.title('Track ID Over Time')
    plt.grid(True, alpha=0.3)
    
    # Track statistics
    unique_tracks = df['track_id'].nunique()
    track_changes = (df['track_id'].diff() != 0).sum()
    
    plt.text(0.02, 0.98, f'Unique Tracks: {unique_tracks}\nTrack Changes: {track_changes}', 
             transform=plt.gca().transAxes, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Frame gaps
    plt.subplot(1, 2, 2)
    frame_diffs = df['frame'].diff()
    gap_frames = frame_diffs[frame_diffs > 1]
    
    if len(gap_frames) > 0:
        plt.hist(gap_frames, bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Frame Gap Size')
        plt.ylabel('Frequency')
        plt.title('Distribution of Frame Gaps')
        plt.grid(True, alpha=0.3)
    else:
        plt.text(0.5, 0.5, 'No frame gaps detected', 
                transform=plt.gca().transAxes, ha='center', va='center',
                fontsize=14, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        plt.title('Frame Gap Analysis')
    
    plt.tight_layout()
    return plt.gcf()

def print_data_summary(df):
    """Print summary statistics of the tracking data."""
    print("\n=== Data Summary ===")
    print(f"Total frames: {len(df)}")
    print(f"Duration: {df['time_s'].max() - df['time_s'].min():.3f} seconds")
    print(f"Average FPS: {len(df) / (df['time_s'].max() - df['time_s'].min()):.1f}")
    
    if 'track_id' in df.columns:
        unique_tracks = df['track_id'].nunique()
        print(f"Unique track IDs: {unique_tracks}")
        print(f"Track ID range: {df['track_id'].min()} to {df['track_id'].max()}")
    
    print(f"Confidence range: {df['conf'].min():.3f} to {df['conf'].max():.3f}")
    print(f"Average confidence: {df['conf'].mean():.3f}")
    
    # Position statistics
    print(f"X position range: {df['cx'].min():.1f} to {df['cx'].max():.1f} pixels")
    print(f"Y position range: {df['cy'].min():.1f} to {df['cy'].max():.1f} pixels")
    
    # Calculate total distance traveled
    if len(df) > 1:
        dx = df['cx'].diff()
        dy = df['cy'].diff()
        distances = np.sqrt(dx**2 + dy**2)
        total_distance = distances.sum()
        print(f"Total distance traveled: {total_distance:.1f} pixels")

def main():
    parser = argparse.ArgumentParser(description='Plot CSV tracking data from ImpulseCV')
    parser.add_argument('csv_file', help='Path to CSV file with tracking data')
    parser.add_argument('--velocity', action='store_true', help='Show velocity vector plot')
    parser.add_argument('--track-analysis', action='store_true', help='Show tracking quality analysis')
    parser.add_argument('--save', help='Save plots to file (specify filename)')
    parser.add_argument('--no-show', action='store_true', help='Don\'t display plots (useful with --save)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"Error: File {args.csv_file} not found")
        return
    
    # Load data
    df = load_and_clean_data(args.csv_file)
    
    # Calculate velocity if not present
    if 'vx' not in df.columns or 'vy' not in df.columns:
        df = calculate_velocity(df)
    
    # Print summary
    print_data_summary(df)
    
    # Create plots
    plots = []
    
    # Main trajectory plot
    fig1 = plot_trajectory(df, f"Ball Trajectory - {os.path.basename(args.csv_file)}")
    plots.append(('trajectory', fig1))
    
    # Velocity vectors plot
    if args.velocity:
        fig2 = plot_velocity_vectors(df)
        plots.append(('velocity', fig2))
    
    # Track analysis plot
    if args.track_analysis:
        fig3 = plot_track_analysis(df)
        if fig3 is not None:
            plots.append(('track_analysis', fig3))
    
    # Save plots if requested
    if args.save:
        base_name = os.path.splitext(args.save)[0]
        for plot_name, fig in plots:
            filename = f"{base_name}_{plot_name}.png"
            fig.savefig(filename, dpi=150, bbox_inches='tight')
            print(f"Saved plot to {filename}")
    
    # Show plots unless --no-show is specified
    if not args.no_show:
        plt.show()
    else:
        plt.close('all')

if __name__ == "__main__":
    main()
