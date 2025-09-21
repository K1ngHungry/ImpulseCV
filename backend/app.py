from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import threading
import time
from werkzeug.utils import secure_filename
from physics_engine import PhysicsEngine
from educational_physics_engine import EducationalPhysicsEngine
from tracking_video_generator import process_video_with_tracking

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

def process_video_background(video_path):
    """Process video in background thread"""
    global processing_status
    
    try:
        processing_status["status"] = "processing"
        processing_status["progress"] = 10
        processing_status["message"] = "Loading video..."
        
        # Check if tracking video already exists
        video_name = os.path.basename(video_path)
        existing_tracking_video = f"static/videos/tracked_{video_name}"
        
        if os.path.exists(existing_tracking_video):
            print(f"✅ Using existing tracking video: tracked_{video_name}")
            tracking_video_path = existing_tracking_video
            csv_path = f"static/videos/tracking_data.csv"
        else:
            processing_status["progress"] = 20
            processing_status["message"] = "Running AI object detection..."
            
            # Generate new tracking video
            csv_path, tracking_video_path = process_video_with_tracking(video_path)
            print(f"✅ Tracking video generated: {os.path.basename(tracking_video_path)}")
        
        processing_status["progress"] = 60
        processing_status["message"] = "Analyzing physics..."
        
        # Load tracking data
        import pandas as pd
        df = pd.read_csv(csv_path)
        
        # Check if we have enough data points for analysis
        if len(df) < 2:
            trajectory_analysis = {"error": "Not enough data points for analysis"}
            physics_insights = {"error": "Not enough data points for analysis"}
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
            global educational_data
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
        
        # Update status with results
        tracking_video_name = os.path.basename(tracking_video_path)
        csv_filename = os.path.basename(csv_path)
        
        processing_status.update({
            "status": "completed",
            "progress": 100,
            "message": f"Processing complete! {len(df)} data points generated.",
            "csv_file": csv_filename,
            "plots": advanced_plots,
            "data_points": len(df),
            "trajectory_analysis": convert_numpy_types(trajectory_analysis),
            "physics_insights": convert_numpy_types(physics_insights),
            "tracking_video": f"videos/{tracking_video_name}",
            "duration": len(df) / 30.0 if len(df) > 0 else 0,  # Estimate duration
            "objects_tracked": len(df['track_id'].unique()) if len(df) > 0 else 0
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

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('assets', exist_ok=True)
    os.makedirs('static/videos', exist_ok=True)
    os.makedirs('static/plots', exist_ok=True)
    
    print("🚀 Starting ImpulseCV API Server...")
    print("📡 API will be available at: http://localhost:8000")
    print("🌐 CORS enabled for React frontend")
    
    app.run(debug=True, host='0.0.0.0', port=8000)