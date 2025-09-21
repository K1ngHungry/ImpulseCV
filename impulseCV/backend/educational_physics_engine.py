"""
Educational Physics Engine for ImpulseCV
Enhanced with learning features, explanations, and interactive demonstrations
"""

# Configure matplotlib backend BEFORE any other imports
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend to avoid threading issues

import numpy as np
import pandas as pd
from scipy import signal
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import json
from typing import Dict, List, Tuple, Any

class EducationalPhysicsEngine:
    def __init__(self, pixels_per_meter=1.0, object_mass=1.0, gravity=9.81):
        """
        Initialize educational physics engine with learning features
        
        Args:
            pixels_per_meter: Conversion factor from pixels to meters
            object_mass: Mass of the tracked object in kg
            gravity: Gravitational acceleration in m/s²
        """
        self.pixels_per_meter = pixels_per_meter
        self.object_mass = object_mass
        self.gravity = gravity
        
        # Physics concepts database
        self.physics_concepts = {
            "kinematics": {
                "velocity": {
                    "definition": "Velocity is the rate of change of position with respect to time. It's a vector quantity with both magnitude (speed) and direction.",
                    "formula": "v = Δx/Δt",
                    "units": "m/s",
                    "real_world_example": "A car moving at 60 km/h has a velocity of 16.7 m/s in the direction it's traveling."
                },
                "acceleration": {
                    "definition": "Acceleration is the rate of change of velocity with respect to time. It indicates how quickly an object's velocity is changing.",
                    "formula": "a = Δv/Δt",
                    "units": "m/s²",
                    "real_world_example": "When you press the gas pedal in a car, you experience acceleration as the car speeds up."
                }
            },
            "dynamics": {
                "force": {
                    "definition": "Force is any interaction that changes the motion of an object. Newton's second law states F = ma.",
                    "formula": "F = ma",
                    "units": "N (Newtons)",
                    "real_world_example": "When you push a shopping cart, you apply a force that makes it move."
                },
                "momentum": {
                    "definition": "Momentum is the product of an object's mass and velocity. It's conserved in isolated systems.",
                    "formula": "p = mv",
                    "units": "kg⋅m/s",
                    "real_world_example": "A heavy truck has more momentum than a bicycle at the same speed."
                }
            },
            "energy": {
                "kinetic_energy": {
                    "definition": "Kinetic energy is the energy an object possesses due to its motion.",
                    "formula": "KE = ½mv²",
                    "units": "J (Joules)",
                    "real_world_example": "A moving baseball has kinetic energy that can break a window."
                },
                "potential_energy": {
                    "definition": "Potential energy is stored energy due to an object's position or configuration.",
                    "formula": "PE = mgh (gravitational)",
                    "units": "J (Joules)",
                    "real_world_example": "A book on a high shelf has gravitational potential energy."
                }
            }
        }
        
        # Common misconceptions and corrections
        self.misconceptions = {
            "velocity_speed": {
                "misconception": "Velocity and speed are the same thing.",
                "correction": "Speed is the magnitude of velocity (how fast), while velocity includes direction (how fast and in what direction)."
            },
            "force_motion": {
                "misconception": "A force is needed to keep an object moving.",
                "correction": "According to Newton's first law, an object in motion stays in motion unless acted upon by an external force (like friction)."
            },
            "energy_work": {
                "misconception": "Work and energy are the same thing.",
                "correction": "Work is the transfer of energy. When you do work on an object, you transfer energy to it."
            }
        }

    def calculate_physics_metrics(self, df):
        """Calculate comprehensive physics metrics with educational context"""
        if len(df) < 2:
            return df
        
        # Create time column if it doesn't exist
        if 'time_s' not in df.columns:
            df['time_s'] = df['frame'] / 30.0
        
        df = df.sort_values('time_s').reset_index(drop=True)
        
        # Convert to meters
        df['x_m'] = df['cx'] / self.pixels_per_meter
        df['y_m'] = df['cy'] / self.pixels_per_meter
        
        # Calculate velocities
        df['velocity_x'] = np.gradient(df['x_m'], df['time_s'])
        df['velocity_y'] = np.gradient(df['y_m'], df['time_s'])
        df['speed'] = np.sqrt(df['velocity_x']**2 + df['velocity_y']**2)
        
        # Calculate accelerations
        df['acceleration_x'] = np.gradient(df['velocity_x'], df['time_s'])
        df['acceleration_y'] = np.gradient(df['velocity_y'], df['time_s'])
        df['acceleration_magnitude'] = np.sqrt(df['acceleration_x']**2 + df['acceleration_y']**2)
        
        # Calculate energies
        df['kinetic_energy'] = 0.5 * self.object_mass * df['speed']**2
        df['potential_energy'] = self.object_mass * self.gravity * df['y_m']
        df['total_energy'] = df['kinetic_energy'] + df['potential_energy']
        
        # Calculate momentum
        df['momentum_x'] = self.object_mass * df['velocity_x']
        df['momentum_y'] = self.object_mass * df['velocity_y']
        df['momentum_magnitude'] = self.object_mass * df['speed']
        
        return df

    def analyze_physics_concepts(self, df):
        """Analyze the motion and identify key physics concepts"""
        if len(df) < 2:
            return {"error": "Not enough data for analysis"}
        
        analysis = {
            "motion_type": self._identify_motion_type(df),
            "key_concepts": [],
            "learning_points": [],
            "common_mistakes": [],
            "real_world_connections": []
        }
        
        # Identify key physics concepts present
        if df['acceleration_magnitude'].max() > 5:  # Significant acceleration
            analysis["key_concepts"].append("acceleration")
            analysis["learning_points"].append("Notice how acceleration changes when forces act on the object")
        
        if df['speed'].max() > 10:  # High speed motion
            analysis["key_concepts"].append("high_speed_motion")
            analysis["learning_points"].append("High speeds result in significant kinetic energy")
        
        # Check for projectile motion
        if self._is_projectile_motion(df):
            analysis["key_concepts"].append("projectile_motion")
            analysis["learning_points"].append("This is projectile motion - the object follows a parabolic path under gravity")
            analysis["real_world_connections"].append("Examples: throwing a ball, shooting a basketball, launching a rocket")
        
        # Energy analysis
        energy_variation = (df['total_energy'].max() - df['total_energy'].min()) / df['total_energy'].mean()
        if energy_variation > 0.1:  # Significant energy change
            analysis["key_concepts"].append("energy_transformation")
            analysis["learning_points"].append("Energy is being transformed between kinetic and potential forms")
            analysis["common_mistakes"].append("Remember: total energy should be conserved in ideal conditions")
        
        return analysis

    def _identify_motion_type(self, df):
        """Identify the type of motion observed"""
        if len(df) < 3:
            return "insufficient_data"
        
        # Check for constant velocity (linear motion)
        velocity_variation = np.std(df['speed']) / np.mean(df['speed'])
        if velocity_variation < 0.1:
            return "constant_velocity"
        
        # Check for projectile motion
        if self._is_projectile_motion(df):
            return "projectile_motion"
        
        # Check for circular motion
        if self._is_circular_motion(df):
            return "circular_motion"
        
        # Check for accelerated motion
        if df['acceleration_magnitude'].mean() > 2:
            return "accelerated_motion"
        
        return "complex_motion"

    def _is_projectile_motion(self, df):
        """Check if the motion resembles projectile motion"""
        if len(df) < 5:
            return False
        
        # Projectile motion has characteristic parabolic trajectory
        # Check if y-position follows a quadratic relationship with x-position
        x = df['x_m'].values
        y = df['y_m'].values
        
        # Fit a quadratic curve
        coeffs = np.polyfit(x, y, 2)
        y_fitted = np.polyval(coeffs, x)
        
        # Calculate R-squared
        ss_res = np.sum((y - y_fitted) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)
        
        return r_squared > 0.8 and coeffs[0] < 0  # Negative coefficient for downward parabola

    def _is_circular_motion(self, df):
        """Check if the motion resembles circular motion"""
        if len(df) < 10:
            return False
        
        # Calculate distance from center
        center_x = np.mean(df['x_m'])
        center_y = np.mean(df['y_m'])
        distances = np.sqrt((df['x_m'] - center_x)**2 + (df['y_m'] - center_y)**2)
        
        # Check if distance from center is relatively constant
        distance_variation = np.std(distances) / np.mean(distances)
        return distance_variation < 0.2

    def generate_educational_explanations(self, df, analysis):
        """Generate educational explanations for the observed motion"""
        explanations = {
            "overview": "",
            "step_by_step": [],
            "formulas_used": [],
            "concept_connections": [],
            "practice_questions": []
        }
        
        motion_type = analysis.get("motion_type", "unknown")
        
        if motion_type == "projectile_motion":
            explanations["overview"] = "You've captured projectile motion! This is a fundamental concept in physics where an object moves under the influence of gravity alone."
            
            explanations["step_by_step"] = [
                "1. The object starts with an initial velocity in both horizontal and vertical directions",
                "2. Gravity acts downward, causing constant vertical acceleration",
                "3. No horizontal force means constant horizontal velocity",
                "4. The combination creates a parabolic trajectory"
            ]
            
            explanations["formulas_used"] = [
                "Horizontal position: x = x₀ + vₓ₀t",
                "Vertical position: y = y₀ + vᵧ₀t - ½gt²",
                "Range: R = (v₀²sin(2θ))/g"
            ]
            
            explanations["concept_connections"] = [
                "This connects to:",
                "• Kinematics (position, velocity, acceleration)",
                "• Vector components (splitting motion into x and y)",
                "• Energy conservation (kinetic ↔ potential)"
            ]
            
            explanations["practice_questions"] = [
                "What would happen if you increased the initial speed?",
                "How would the trajectory change on the Moon (lower gravity)?",
                "At what angle should you launch for maximum range?"
            ]
        
        elif motion_type == "constant_velocity":
            explanations["overview"] = "This shows constant velocity motion - a key example of Newton's First Law in action!"
            
            explanations["step_by_step"] = [
                "1. The object moves at a steady speed in a straight line",
                "2. No net force is acting on the object",
                "3. This demonstrates inertia - objects resist changes in motion"
            ]
            
            explanations["formulas_used"] = [
                "Position: x = x₀ + vt",
                "Velocity: v = constant"
            ]
        
        return explanations

    def create_learning_quiz(self, df, analysis):
        """Create a quiz based on the observed motion"""
        quiz = {
            "questions": [],
            "difficulty": "beginner",
            "concepts_tested": []
        }
        
        motion_type = analysis.get("motion_type", "unknown")
        
        if motion_type == "projectile_motion":
            quiz["questions"] = [
                {
                    "question": "What type of motion is shown in this video?",
                    "options": ["Linear motion", "Projectile motion", "Circular motion", "Random motion"],
                    "correct": 1,
                    "explanation": "The parabolic trajectory indicates projectile motion under gravity."
                },
                {
                    "question": "What force is primarily acting on the object?",
                    "options": ["Air resistance", "Gravity", "Friction", "Applied force"],
                    "correct": 1,
                    "explanation": "In projectile motion, gravity is the main force acting downward."
                },
                {
                    "question": "Why does the object follow a curved path?",
                    "options": [
                        "Because it's spinning",
                        "Because gravity pulls it downward while it moves forward",
                        "Because of air resistance",
                        "Because it's magnetic"
                    ],
                    "correct": 1,
                    "explanation": "The horizontal motion continues while gravity pulls the object downward, creating a parabola."
                }
            ]
            quiz["concepts_tested"] = ["projectile_motion", "gravity", "trajectory"]
        
        return quiz

    def generate_visual_learning_aids(self, df, output_dir="static/plots"):
        """Generate visual aids for learning"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        plots = {}
        
        # Create concept visualization plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Physics Learning Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Position vs Time
        axes[0, 0].plot(df['time_s'], df['x_m'], 'b-', label='X Position', linewidth=2)
        axes[0, 0].plot(df['time_s'], df['y_m'], 'r-', label='Y Position', linewidth=2)
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Position (m)')
        axes[0, 0].set_title('Position vs Time')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Velocity vs Time
        axes[0, 1].plot(df['time_s'], df['velocity_x'], 'b-', label='Vx', linewidth=2)
        axes[0, 1].plot(df['time_s'], df['velocity_y'], 'r-', label='Vy', linewidth=2)
        axes[0, 1].plot(df['time_s'], df['speed'], 'g-', label='Speed', linewidth=2)
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Velocity (m/s)')
        axes[0, 1].set_title('Velocity vs Time')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Energy vs Time
        axes[1, 0].plot(df['time_s'], df['kinetic_energy'], 'b-', label='Kinetic Energy', linewidth=2)
        axes[1, 0].plot(df['time_s'], df['potential_energy'], 'r-', label='Potential Energy', linewidth=2)
        axes[1, 0].plot(df['time_s'], df['total_energy'], 'g-', label='Total Energy', linewidth=2)
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Energy (J)')
        axes[1, 0].set_title('Energy vs Time')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Trajectory
        axes[1, 1].plot(df['x_m'], df['y_m'], 'b-', linewidth=3, label='Trajectory')
        axes[1, 1].scatter(df['x_m'].iloc[0], df['y_m'].iloc[0], color='green', s=100, label='Start', zorder=5)
        axes[1, 1].scatter(df['x_m'].iloc[-1], df['y_m'].iloc[-1], color='red', s=100, label='End', zorder=5)
        axes[1, 1].set_xlabel('X Position (m)')
        axes[1, 1].set_ylabel('Y Position (m)')
        axes[1, 1].set_title('Object Trajectory')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].set_aspect('equal')
        
        plt.tight_layout()
        learning_plot_path = os.path.join(output_dir, 'learning_dashboard.png')
        plt.savefig(learning_plot_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        plots['learning_dashboard'] = learning_plot_path
        
        return plots

    def get_concept_explanation(self, concept_category, concept_name):
        """Get detailed explanation of a physics concept"""
        if concept_category in self.physics_concepts and concept_name in self.physics_concepts[concept_category]:
            return self.physics_concepts[concept_category][concept_name]
        return None

    def get_misconception_correction(self, misconception_key):
        """Get correction for a common misconception"""
        if misconception_key in self.misconceptions:
            return self.misconceptions[misconception_key]
        return None
