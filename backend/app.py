from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import threading
import time
from werkzeug.utils import secure_filename
from physics_engine import PhysicsEngine
from educational_physics_engine import EducationalPhysicsEngine
from tracking_video_generator import process_video_with_tracking
from data_cleaner import DataCleaner

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
app.config['UPLOAD_FOLDER'] = 'assets'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Global processing status
processing_status = {
    "status": "idle",
    "progress": 0,
    "message": "Ready to analyze videos",
    "data_points": 0,
    "plots": {},
    "trajectory_analysis": {},
    "physics_insights": {},
    "csv_file": None,
    "tracking_video": None
}

# Global educational data
educational_data = None

# Global motion explanation
motion_explanation = None

def convert_numpy_types(obj):
    """Convert NumPy types to Python types for JSON serialization"""
    import numpy as np
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

def generate_motion_explanation(df, analysis):
    """Generate a simple motion explanation paragraph"""
    import numpy as np
    
    if len(df) < 2:
        return "Insufficient data for motion analysis. Please ensure the video contains clear object movement."
    
    # Extract key metrics safely
    motion_type = analysis.get('motion_type', 'unknown')
    duration = df['time_s'].max() - df['time_s'].min() if len(df) > 1 else 0
    
    # Safely get velocity metrics
    if 'speed' in df.columns:
        max_velocity = df['speed'].max()
    elif 'velocity_x' in df.columns and 'velocity_y' in df.columns:
        # Calculate speed from velocity components
        speed = np.sqrt(df['velocity_x']**2 + df['velocity_y']**2)
        max_velocity = speed.max()
    else:
        max_velocity = 0
    
    # Safely get acceleration metrics
    if 'acceleration_magnitude' in df.columns:
        max_acceleration = df['acceleration_magnitude'].max()
    elif 'acceleration_x' in df.columns and 'acceleration_y' in df.columns:
        # Calculate acceleration magnitude from components
        accel_mag = np.sqrt(df['acceleration_x']**2 + df['acceleration_y']**2)
        max_acceleration = accel_mag.max()
    else:
        max_acceleration = 0
    
    # Determine object type and color (simplified detection)
    if max_velocity > 20:
        object_type = "ball"
        object_color = "yellow"  # Default assumption for now
    else:
        object_type = "object"
        object_color = "tracked"
    
    # Analyze velocity and acceleration patterns for more specific descriptions
    if 'velocity_x' in df.columns and 'velocity_y' in df.columns:
        # Check if horizontal velocity is roughly constant (projectile motion)
        vx_std = np.std(df['velocity_x'])
        vx_mean = np.abs(np.mean(df['velocity_x']))
        horizontal_constant = vx_std / vx_mean < 0.4 if vx_mean > 0.1 else False
        
        # Check if vertical velocity is changing (due to gravity)
        vy_change = np.max(df['velocity_y']) - np.min(df['velocity_y'])
        vertical_acceleration = vy_change > 3  # Significant change in vertical velocity
        
        # Check if there's a clear trajectory (height changes significantly)
        if 'y_m' in df.columns:
            height_change = np.max(df['y_m']) - np.min(df['y_m'])
            has_trajectory = height_change > 2  # Significant height change
        else:
            has_trajectory = False
    else:
        horizontal_constant = False
        vertical_acceleration = False
        has_trajectory = False
    
    # Generate detailed physics explanations based on motion type and patterns
    if motion_type == 'projectile_motion' or (horizontal_constant and vertical_acceleration and has_trajectory):
        return f"""The {object_color} {object_type} is being thrown up into the air and experiences projectile motion. The {object_type} moves forward at a constant speed while gravity simultaneously pulls it downward, causing it to rise, reach a peak, then fall back down. These two motions combine to create the familiar arc-shaped trajectory you see whenever you throw any object through the air."""
    
    elif motion_type == 'constant_velocity':
        return f"""The {object_color} {object_type} is moving at constant velocity. The {object_type} travels in a straight line at steady speed with no acceleration, demonstrating Newton's First Law where an object in motion stays in motion unless acted upon by an external force. This indicates that friction and air resistance are negligible, allowing the {object_type} to maintain its motion indefinitely."""
    
    elif motion_type == 'circular_motion':
        return f"""The {object_color} {object_type} is following circular motion. The {object_type} moves in a curved path at constant speed but with continuously changing direction. This is caused by centripetal forces that pull the {object_type} toward the center of the circle, creating the circular path. The acceleration is always directed toward the center, changing the {object_type}'s direction without changing its speed."""
    
    elif max_velocity > 30 and has_trajectory:
        return f"""The {object_color} {object_type} is being thrown up into the air and experiences projectile motion. The {object_type} moves forward at a constant speed while gravity simultaneously pulls it downward, causing it to rise, reach a peak, then fall back down. These two motions combine to create the familiar arc-shaped trajectory you see whenever you throw any object through the air."""
    
    elif max_velocity > 15:
        return f"""The {object_color} {object_type} is moving at high speed through the air. The {object_type} experiences the combined effects of its initial velocity and gravity, with air resistance gradually slowing it down. As it travels, gravity continuously pulls it downward while air resistance opposes its motion, creating a curved path that becomes steeper over time."""
    
    else:
        return f"""The {object_color} {object_type} is moving with varying motion. The {object_type} shows changing velocity patterns as it moves, with its motion being influenced by gravity, friction, and other forces acting upon it. The acceleration changes indicate that multiple forces are interacting with the {object_type}, creating complex motion that demonstrates the interplay between different physical forces."""

def process_video_background(video_path):
    """Process video in background thread"""
    global processing_status
    
    try:
        processing_status["status"] = "processing"
        processing_status["progress"] = 10
        processing_status["message"] = "Loading video..."
        
        # Always regenerate tracking video with new vector visualization
        video_name = os.path.basename(video_path)
        processing_status["progress"] = 20
        processing_status["message"] = "Running AI object detection with force vectors..."
        
        # Generate new tracking video with physics vectors
        csv_path, tracking_video_path = process_video_with_tracking(video_path)
        print(f"✅ Tracking video with force vectors generated: {os.path.basename(tracking_video_path)}")
        
        processing_status["progress"] = 60
        processing_status["message"] = "Analyzing physics..."
        
        # Load tracking data
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        # Clean the data to remove outliers
        processing_status["progress"] = 50
        processing_status["message"] = "Cleaning data and removing outliers..."
        
        data_cleaner = DataCleaner(
            max_gap=1,
            k_speed=4.0,
            k_back=3.5,
            back_min=15.0,
            cx_tol=8.0,
            k_resid=3.5,
            trim_passes=3,
            invert=False
        )
        
        df_cleaned, cleaning_stats = data_cleaner.clean_all_tracks(df)
        
        # Save cleaned data
        cleaned_csv_path = csv_path.replace('.csv', '_cleaned.csv')
        df_cleaned.to_csv(cleaned_csv_path, index=False)
        
        print(f"✅ Data cleaning complete: {len(df)} → {len(df_cleaned)} points ({cleaning_stats.get('cleaning_percentage', 0):.1f}% outliers removed)")
        
        # Use cleaned data for analysis
        df = df_cleaned
        
        # Check if we have enough data points for analysis
        if len(df) < 2:
            trajectory_analysis = {"error": "Not enough data points for analysis after cleaning"}
            physics_insights = {"error": "Not enough data points for analysis after cleaning"}
            advanced_plots = {}
        else:
            # Initialize physics engine and calculate advanced metrics
            physics_engine = PhysicsEngine(pixels_per_meter=50.0, object_mass=0.5)
            df = physics_engine.calculate_physics_metrics(df)
            
            # Analyze trajectory and generate insights (after physics calculations)
            trajectory_analysis = physics_engine.analyze_trajectory(df)
            physics_insights = physics_engine.calculate_physics_insights(df)
            
            processing_status["progress"] = 80
            processing_status["message"] = "Generating visualizations..."
            
            # Generate advanced physics plots
            advanced_plots = physics_engine.generate_advanced_plots(df)
            
            # Generate educational analysis
            global educational_data, motion_explanation
            educational_engine = EducationalPhysicsEngine(pixels_per_meter=50.0, object_mass=0.5)
            # Calculate physics metrics first
            df_enhanced = educational_engine.calculate_physics_metrics(df)
            educational_analysis = educational_engine.analyze_physics_concepts(df_enhanced)
            educational_explanations = educational_engine.generate_educational_explanations(df_enhanced, educational_analysis)
            educational_quiz = educational_engine.create_learning_quiz(df_enhanced, educational_analysis)
            educational_plots = educational_engine.generate_visual_learning_aids(df_enhanced)
            
            educational_data = {
                "analysis": educational_analysis,
                "explanations": educational_explanations,
                "quiz": educational_quiz,
                "plots": educational_plots
            }
            
            # Generate motion explanation
            motion_explanation = generate_motion_explanation(df_enhanced, educational_analysis)
        
        # Update status with results
        tracking_video_name = os.path.basename(tracking_video_path)
        csv_filename = os.path.basename(csv_path)
        cleaned_csv_filename = os.path.basename(cleaned_csv_path) if 'cleaned_csv_path' in locals() else None
        
        processing_status.update({
            "status": "completed",
            "progress": 100,
            "message": f"Processing complete! {len(df)} data points generated.",
            "csv_file": csv_filename,
            "cleaned_csv_file": cleaned_csv_filename,
            "plots": advanced_plots,
            "data_points": len(df),
            "trajectory_analysis": convert_numpy_types(trajectory_analysis),
            "physics_insights": convert_numpy_types(physics_insights),
            "tracking_video": f"videos/{tracking_video_name}",
            "duration": len(df) / 30.0 if len(df) > 0 else 0,  # Estimate duration
            "objects_tracked": len(df['track_id'].unique()) if len(df) > 0 else 0,
            "cleaning_stats": convert_numpy_types(cleaning_stats) if 'cleaning_stats' in locals() else {}
        })
        
        print(f"✅ Processing complete: {len(df)} data points, {len(advanced_plots)} plots")
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()
        processing_status.update({
            "status": "error",
            "message": f"Processing failed: {str(e)}"
        })

@app.route('/')
def index():
    """API health check"""
    return jsonify({
        "message": "ImpulseCV API",
        "status": "running",
        "version": "1.0.0"
    })

@app.route('/status')
def get_status():
    """Get current processing status"""
    return jsonify(processing_status)

@app.route('/assets')
def list_assets():
    """List available video assets"""
    assets = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                assets.append(file)
    return jsonify(assets)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a new video file and start processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Start processing the uploaded file
        global processing_status
        processing_status = {
            "status": "processing",
            "progress": 0,
            "message": "Starting video processing...",
            "data_points": 0,
            "physics_insights": {},
            "plots": {},
            "trajectory_analysis": {},
            "tracking_video": None,
            "csv_file": None
        }
        
        # Start background processing
        thread = threading.Thread(target=process_video_background, args=(filepath,))
        thread.daemon = True
        thread.start()
        
        return jsonify({'filename': filename, 'path': filepath, 'message': 'Upload successful, processing started'})

@app.route('/process_asset/<filename>')
def process_asset(filename):
    """Process a specific asset file"""
    global processing_status
    
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(video_path):
        return jsonify({'error': 'File not found'}), 404
    
    # Reset processing status
    processing_status = {
        "status": "processing",
        "progress": 0,
        "message": "Starting video processing...",
        "data_points": 0,
        "plots": {},
        "trajectory_analysis": {},
        "physics_insights": {},
        "csv_file": None,
        "tracking_video": None
    }
    
    # Start processing in background
    thread = threading.Thread(target=process_video_background, args=(video_path,))
    thread.daemon = True
    thread.start()
    
    return jsonify({'message': 'Processing started', 'filename': filename})

@app.route('/download/<filename>')
def download_file(filename):
    """Download a file"""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/download_cleaned/<filename>')
def download_cleaned_file(filename):
    """Download cleaned CSV data"""
    # Look for cleaned version first
    cleaned_filename = filename.replace('.csv', '_cleaned.csv')
    cleaned_path = os.path.join('static', 'videos', cleaned_filename)
    
    if os.path.exists(cleaned_path):
        return send_file(cleaned_path, as_attachment=True)
    else:
        # Fallback to original file
        original_path = os.path.join('static', 'videos', filename)
        if os.path.exists(original_path):
            return send_file(original_path, as_attachment=True)
        else:
            return jsonify({'error': 'File not found'}), 404

@app.route('/videos/<filename>')
def serve_video(filename):
    """Serve tracking videos"""
    video_path = os.path.join('static', 'videos', filename)
    if os.path.exists(video_path):
        return send_file(video_path)
    else:
        return jsonify({'error': 'Video not found'}), 404

@app.route('/plots/<filename>')
def serve_plot(filename):
    """Serve plot images"""
    plot_path = os.path.join('static', 'plots', filename)
    if os.path.exists(plot_path):
        return send_file(plot_path)
    else:
        return jsonify({'error': 'Plot not found'}), 404

@app.route('/educational_analysis')
def get_educational_analysis():
    """Get educational analysis data"""
    global educational_data
    if educational_data:
        return jsonify(convert_numpy_types(educational_data))
    else:
        return jsonify({'error': 'No educational analysis available'}), 404

@app.route('/motion_explanation')
def get_motion_explanation():
    """Get motion explanation"""
    global motion_explanation
    if motion_explanation:
        return jsonify({'explanation': motion_explanation})
    else:
        return jsonify({'error': 'No motion explanation available'}), 404

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('assets', exist_ok=True)
    os.makedirs('static/videos', exist_ok=True)
    os.makedirs('static/plots', exist_ok=True)
    
    print("🚀 Starting ImpulseCV API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("🌐 CORS enabled for React frontend")
    
    app.run(debug=True, host='0.0.0.0', port=8000)