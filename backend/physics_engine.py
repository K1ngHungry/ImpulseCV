"""
Advanced Physics Engine for ImpulseCV
Calculates velocity, acceleration, forces, energy, and other physics metrics
"""

# Configure matplotlib backend BEFORE any other imports
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid threading issues

import numpy as np
import pandas as pd
from scipy import signal
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

class PhysicsEngine:
    def __init__(self, pixels_per_meter=1.0, object_mass=1.0, gravity=9.81):
        """
        Initialize physics engine with calibration parameters
        
        Args:
            pixels_per_meter: Conversion factor from pixels to meters
            object_mass: Mass of the tracked object in kg
            gravity: Gravitational acceleration in m/s²
        """
        self.pixels_per_meter = pixels_per_meter
        self.object_mass = object_mass
        self.gravity = gravity
        
    def calculate_physics_metrics(self, df):
        """
        Calculate comprehensive physics metrics from tracking data
        
        Args:
            df: DataFrame with tracking data
            
        Returns:
            Enhanced DataFrame with physics calculations
        """
        if len(df) < 2:
            return df
        
        # Create time column if it doesn't exist (assuming 30 FPS)
        if 'time_s' not in df.columns:
            df['time_s'] = df['frame'] / 30.0
        
        # Sort by time
        df = df.sort_values('time_s').reset_index(drop=True)
        
        # Convert to meters
        df['cx_m'] = df['cx'] / self.pixels_per_meter
        df['cy_m'] = df['cy'] / self.pixels_per_meter
        
        # Calculate velocity (m/s) with safe division
        time_diff = df['time_s'].diff()
        df['vx_m'] = df['cx_m'].diff() / time_diff.replace(0, np.nan)
        df['vy_m'] = df['cy_m'].diff() / time_diff.replace(0, np.nan)
        
        # Calculate acceleration (m/s²) with safe division
        df['ax_m'] = df['vx_m'].diff() / time_diff.replace(0, np.nan)
        df['ay_m'] = df['vy_m'].diff() / time_diff.replace(0, np.nan)
        
        # Calculate magnitude quantities (handle infinite values)
        df['speed_m'] = np.sqrt(np.nan_to_num(df['vx_m']**2) + np.nan_to_num(df['vy_m']**2))
        df['acceleration_m'] = np.sqrt(np.nan_to_num(df['ax_m']**2) + np.nan_to_num(df['ay_m']**2))
        
        # Calculate kinetic energy (J) - handle infinite values
        df['kinetic_energy'] = 0.5 * self.object_mass * np.nan_to_num(df['speed_m']**2)
        
        # Calculate momentum (kg⋅m/s) - handle infinite values
        df['momentum_x'] = self.object_mass * np.nan_to_num(df['vx_m'])
        df['momentum_y'] = self.object_mass * np.nan_to_num(df['vy_m'])
        df['momentum_magnitude'] = self.object_mass * np.nan_to_num(df['speed_m'])
        
        # Calculate forces (N) - handle infinite values
        df['force_x'] = self.object_mass * np.nan_to_num(df['ax_m'])
        df['force_y'] = self.object_mass * np.nan_to_num(df['ay_m'])
        df['force_magnitude'] = self.object_mass * np.nan_to_num(df['acceleration_m'])
        
        # Calculate potential energy (J) - assuming ground is at bottom of frame
        max_height = df['cy_m'].max()
        df['potential_energy'] = self.object_mass * self.gravity * (max_height - df['cy_m'])
        
        # Calculate total energy (J)
        df['total_energy'] = df['kinetic_energy'] + df['potential_energy']
        
        # Calculate work done (J)
        df['work_done'] = df['total_energy'].diff()
        
        # Calculate power (W) - handle infinite values
        time_diff_power = df['time_s'].diff().replace(0, np.nan)
        df['power'] = df['work_done'] / time_diff_power
        
        # Smooth the data using Savitzky-Golay filter
        df = self.smooth_data(df)
        
        # Fill NaN values
        df = df.fillna(0)
        
        return df
    
    def smooth_data(self, df, window_length=5):
        """
        Apply Savitzky-Golay filter to smooth noisy data
        
        Args:
            df: DataFrame with physics data
            window_length: Window length for smoothing filter
            
        Returns:
            Smoothed DataFrame
        """
        if len(df) < window_length:
            return df
        
        # Ensure window_length is odd and not larger than data length
        if window_length % 2 == 0:
            window_length += 1
        if window_length > len(df):
            window_length = len(df) if len(df) % 2 == 1 else len(df) - 1
            
        try:
            # Smooth position data
            df['cx_m_smooth'] = signal.savgol_filter(df['cx_m'], window_length, min(3, window_length-1))
            df['cy_m_smooth'] = signal.savgol_filter(df['cy_m'], window_length, min(3, window_length-1))
            
            # Recalculate velocity from smoothed position with safe gradient
            df['vx_m_smooth'] = self.safe_gradient(df['cx_m_smooth'], df['time_s'])
            df['vy_m_smooth'] = self.safe_gradient(df['cy_m_smooth'], df['time_s'])
            
            # Recalculate acceleration from smoothed velocity with safe gradient
            df['ax_m_smooth'] = self.safe_gradient(df['vx_m_smooth'], df['time_s'])
            df['ay_m_smooth'] = self.safe_gradient(df['vy_m_smooth'], df['time_s'])
            
        except Exception as e:
            # Fallback to simple smoothing if Savitzky-Golay fails
            df['cx_m_smooth'] = df['cx_m']
            df['cy_m_smooth'] = df['cy_m']
            df['vx_m_smooth'] = df['vx_m']
            df['vy_m_smooth'] = df['vy_m']
            df['ax_m_smooth'] = df['ax_m']
            df['ay_m_smooth'] = df['ay_m']
        
        return df
    
    def safe_gradient(self, y, x):
        """
        Calculate gradient safely handling edge cases
        
        Args:
            y: y values
            x: x values
            
        Returns:
            Gradient array
        """
        if len(y) < 2:
            return np.zeros_like(y)
        
        # Remove any NaN or infinite values
        mask = np.isfinite(y) & np.isfinite(x)
        if not np.any(mask):
            return np.zeros_like(y)
        
        # Calculate gradient with finite difference
        gradient = np.zeros_like(y, dtype=float)
        
        for i in range(len(y)):
            if i == 0:
                # Forward difference
                if len(y) > 1:
                    dx = x[1] - x[0]
                    dy = y[1] - y[0]
                    if dx != 0:
                        gradient[i] = dy / dx
            elif i == len(y) - 1:
                # Backward difference
                dx = x[i] - x[i-1]
                dy = y[i] - y[i-1]
                if dx != 0:
                    gradient[i] = dy / dx
            else:
                # Central difference
                dx = x[i+1] - x[i-1]
                dy = y[i+1] - y[i-1]
                if dx != 0:
                    gradient[i] = dy / dx
        
        return gradient
    
    def analyze_trajectory(self, df):
        """
        Analyze trajectory characteristics
        
        Args:
            df: DataFrame with physics data
            
        Returns:
            Dictionary with trajectory analysis
        """
        analysis = {}
        
        # Basic trajectory info
        analysis['total_distance'] = np.sum(np.sqrt(np.diff(df['cx_m'])**2 + np.diff(df['cy_m'])**2))
        analysis['max_height'] = df['cy_m'].max()
        analysis['min_height'] = df['cy_m'].min()
        analysis['horizontal_range'] = df['cx_m'].max() - df['cx_m'].min()
        analysis['duration'] = df['time_s'].max() - df['time_s'].min()
        
        # Velocity analysis (handle infinite values)
        analysis['max_speed'] = np.nanmax(np.nan_to_num(df['speed_m']))
        analysis['avg_speed'] = np.nanmean(np.nan_to_num(df['speed_m']))
        analysis['max_velocity_x'] = np.nanmax(np.nan_to_num(df['vx_m']))
        analysis['max_velocity_y'] = np.nanmax(np.nan_to_num(df['vy_m']))
        
        # Acceleration analysis (handle infinite values)
        analysis['max_acceleration'] = np.nanmax(np.nan_to_num(df['acceleration_m']))
        analysis['avg_acceleration'] = np.nanmean(np.nan_to_num(df['acceleration_m']))
        
        # Energy analysis
        analysis['max_kinetic_energy'] = df['kinetic_energy'].max()
        analysis['max_potential_energy'] = df['potential_energy'].max()
        analysis['energy_conservation_error'] = np.std(df['total_energy'])
        
        # Check for projectile motion
        analysis['is_projectile'] = self.detect_projectile_motion(df)
        
        return analysis
    
    def detect_projectile_motion(self, df):
        """
        Detect if motion follows projectile motion patterns
        
        Args:
            df: DataFrame with physics data
            
        Returns:
            Boolean indicating if motion is projectile-like
        """
        if len(df) < 10:
            return False
            
        # Check for parabolic trajectory
        x = df['cx_m'].values
        y = df['cy_m'].values
        
        # Fit quadratic curve
        coeffs = np.polyfit(x, y, 2)
        
        # Calculate R²
        y_pred = np.polyval(coeffs, x)
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        # Check if acceleration is roughly constant in y-direction
        y_acceleration = df['ay_m'].mean()
        acceleration_variance = np.var(df['ay_m'])
        
        return r_squared > 0.8 and abs(y_acceleration + self.gravity) < 5 and acceleration_variance < 10
    
    def calculate_physics_insights(self, df):
        """
        Generate physics insights and explanations
        
        Args:
            df: DataFrame with physics data
            
        Returns:
            List of physics insights
        """
        insights = []
        
        # Energy conservation
        energy_error = np.std(df['total_energy'])
        if energy_error < 1:
            insights.append("✅ Excellent energy conservation - motion is nearly frictionless")
        elif energy_error < 5:
            insights.append("⚠️ Moderate energy loss - some friction or air resistance present")
        else:
            insights.append("❌ Significant energy loss - high friction or external forces")
        
        # Projectile motion
        if self.detect_projectile_motion(df):
            insights.append("🎯 Perfect projectile motion detected - parabolic trajectory")
            max_height = df['cy_m'].max()
            horizontal_range = df['cx_m'].max() - df['cx_m'].min()
            insights.append(f"📏 Maximum height: {max_height:.2f}m, Range: {horizontal_range:.2f}m")
        
        # Acceleration analysis
        avg_acceleration = df['acceleration_m'].mean()
        if abs(avg_acceleration - self.gravity) < 2:
            insights.append("🌍 Acceleration matches gravitational acceleration")
        elif avg_acceleration > self.gravity + 2:
            insights.append("🚀 Above-average acceleration - external forces present")
        
        # Speed analysis
        max_speed = df['speed_m'].max()
        if max_speed > 10:
            insights.append(f"🏃 High-speed motion detected: {max_speed:.1f} m/s")
        elif max_speed < 1:
            insights.append(f"🐌 Slow motion: {max_speed:.1f} m/s")
        
        return insights
    
    def generate_advanced_plots(self, df, output_dir='static/plots'):
        """
        Generate advanced physics visualization plots
        
        Args:
            df: DataFrame with physics data
            output_dir: Directory to save plots
            
        Returns:
            Dictionary with plot file paths
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        plots = {}
        
        # Energy plot
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.plot(df['time_s'], df['kinetic_energy'], 'b-', label='Kinetic Energy', linewidth=2)
        plt.plot(df['time_s'], df['potential_energy'], 'r-', label='Potential Energy', linewidth=2)
        plt.plot(df['time_s'], df['total_energy'], 'g-', label='Total Energy', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Energy (J)')
        plt.title('Energy Analysis')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 2)
        plt.plot(df['time_s'], df['force_magnitude'], 'purple', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Force (N)')
        plt.title('Force Magnitude')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 3)
        plt.plot(df['time_s'], df['power'], 'orange', linewidth=2)
        plt.xlabel('Time (s)')
        plt.ylabel('Power (W)')
        plt.title('Power vs Time')
        plt.grid(True, alpha=0.3)
        
        plt.subplot(2, 2, 4)
        plt.plot(df['cx_m'], df['cy_m'], 'b-', linewidth=2, label='Trajectory')
        plt.scatter(df['cx_m'].iloc[0], df['cy_m'].iloc[0], color='green', s=100, label='Start', zorder=5)
        plt.scatter(df['cx_m'].iloc[-1], df['cy_m'].iloc[-1], color='red', s=100, label='End', zorder=5)
        plt.xlabel('X Position (m)')
        plt.ylabel('Y Position (m)')
        plt.title('Trajectory in Real Units')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.gca().invert_yaxis()
        
        plt.tight_layout()
        plot_path = os.path.join(output_dir, 'advanced_physics.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        plots['advanced_physics'] = plot_path
        
        # Phase space plot
        plt.figure(figsize=(10, 6))
        plt.plot(df['cx_m'], df['vx_m'], 'b-', linewidth=2, label='X Phase Space')
        plt.plot(df['cy_m'], df['vy_m'], 'r-', linewidth=2, label='Y Phase Space')
        plt.xlabel('Position (m)')
        plt.ylabel('Velocity (m/s)')
        plt.title('Phase Space Plot')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plot_path = os.path.join(output_dir, 'phase_space.png')
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        plots['phase_space'] = plot_path
        
        return plots
