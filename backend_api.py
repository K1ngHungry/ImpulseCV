#!/usr/bin/env python3
"""
Backend API for ImpulseCV Frontend
Provides REST API endpoints for video analysis and data retrieval.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import json
import subprocess
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_analysis(video_path: str, config: Dict[str, Any]) -> str:
    """Run the tracking analysis on the uploaded video."""
    
    # Generate unique result filename
    result_id = str(uuid.uuid4())
    result_csv = os.path.join(RESULTS_FOLDER, f"{result_id}_data.csv")
    
    # Create temporary analysis script
    analysis_script = f"""
from ultralytics import YOLO
import cv2, csv
import pandas as pd
import numpy as np

# Configuration
model = YOLO('yolov8n.pt')
video_path = '{video_path}'
result_csv = '{result_csv}'

# Analysis parameters
CONF = {config.get('confidence', 0.15)}
IOU = {config.get('iouThreshold', 0.5)}
IMGZ = {config.get('inputSize', 960)}
TARGET = {config.get('objectClass', 32)}

# Load video
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

data = []
frame_idx = 0

while True:
    ok, frame = cap.read()
    if not ok:
        break
    frame_idx += 1
    t_sec = frame_idx / fps

    # Run tracking
    results = model.track(
        frame,
        persist=True,
        tracker="bytetrack.yaml",
        conf=CONF,
        iou=IOU,
        imgsz=IMGZ,
        classes=[TARGET] if TARGET is not None else None,
        verbose=False
    )

    r = results[0]

    # Collect data
    if r.boxes is not None and len(r.boxes):
        boxes = r.boxes
        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i])
            if TARGET is not None and cls_id != TARGET:
                continue
            track_id = int(boxes.id[i]) if boxes.id is not None else -1
            conf = float(boxes.conf[i])
            x1, y1, x2, y2 = map(float, boxes.xyxy[i].tolist())
            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

            data.append([
                frame_idx, t_sec, track_id, cls_id, 'sports ball',
                conf, x1, y1, x2, y2, cx, cy
            ])

cap.release()

# Save raw data
with open(result_csv, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow([
        'frame','time_s','track_id','class_id','class_name','conf',
        'x1','y1','x2','y2','cx','cy'
    ])
    w.writerows(data)

print(f"Analysis complete: {{len(data)}} detections saved to {{result_csv}}")
"""
    
    # Write and execute analysis script
    script_path = os.path.join(RESULTS_FOLDER, f"{result_id}_analysis.py")
    with open(script_path, 'w') as f:
        f.write(analysis_script)
    
    try:
        # Run analysis
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        if result.returncode != 0:
            raise Exception(f"Analysis failed: {result.stderr}")
        
        # Clean up script
        os.remove(script_path)
        
        return result_csv
        
    except Exception as e:
        # Clean up on error
        if os.path.exists(script_path):
            os.remove(script_path)
        raise e

def process_analysis_results(csv_path: str, video_path: str = None) -> Dict[str, Any]:
    """Process the CSV results and return formatted data for frontend."""
    
    # Read the CSV data
    df = pd.read_csv(csv_path)
    
    if len(df) == 0:
        return {
            'error': 'No tracking data found'
        }
    
    # Get video dimensions if video path is provided
    video_info = {}
    if video_path and os.path.exists(video_path):
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                video_info = {
                    'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'fps': cap.get(cv2.CAP_PROP_FPS),
                    'frameCount': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                }
                cap.release()
        except Exception as e:
            print(f"Warning: Could not get video info: {e}")
            # Default dimensions
            video_info = {'width': 1920, 'height': 1080, 'fps': 30}
    else:
        # Default dimensions
        video_info = {'width': 1920, 'height': 1080, 'fps': 30}
    
    # Calculate velocities
    df = df.sort_values('frame').reset_index(drop=True)
    df['vx'] = df['cx'].diff()
    df['vy'] = df['cy'].diff()
    df['velocity'] = np.sqrt(df['vx']**2 + df['vy']**2)
    
    # Calculate accelerations
    df['ax'] = df['vx'].diff()
    df['ay'] = df['vy'].diff()
    df['acceleration'] = np.sqrt(df['ax']**2 + df['ay']**2)
    
    # Convert to trajectory points
    trajectory = []
    for _, row in df.iterrows():
        trajectory.append({
            'frame': int(row['frame']),
            'time': float(row['time_s']),
            'x': float(row['cx']),
            'y': float(row['cy']),
            'vx': float(row['vx']) if not pd.isna(row['vx']) else 0,
            'vy': float(row['vy']) if not pd.isna(row['vy']) else 0,
            'velocity': float(row['velocity']) if not pd.isna(row['velocity']) else 0,
            'confidence': float(row['conf']),
            'trackId': int(row['track_id'])
        })
    
    # Calculate statistics
    fps = len(df) / df['time_s'].max() if df['time_s'].max() > 0 else 0
    
    statistics = {
        'totalDistance': float(df['velocity'].sum()),
        'maxVelocity': float(df['velocity'].max()) if not df['velocity'].isna().all() else 0,
        'avgVelocity': float(df['velocity'].mean()) if not df['velocity'].isna().all() else 0,
        'maxAcceleration': float(df['acceleration'].max()) if not df['acceleration'].isna().all() else 0,
        'avgAcceleration': float(df['acceleration'].mean()) if not df['acceleration'].isna().all() else 0,
        'xRange': [float(df['cx'].min()), float(df['cx'].max())],
        'yRange': [float(df['cy'].min()), float(df['cy'].max())]
    }
    
    confidence_stats = {
        'min': float(df['conf'].min()),
        'max': float(df['conf'].max()),
        'average': float(df['conf'].mean())
    }
    
    # Get unique track IDs
    track_ids = sorted([int(x) for x in df['track_id'].unique() if x != -1])
    
    return {
        'frames': len(df),
        'duration': float(df['time_s'].max()),
        'fps': fps,
        'trajectory': trajectory,
        'statistics': statistics,
        'trackIds': track_ids,
        'confidence': confidence_stats,
        'videoInfo': video_info
    }

@app.route('/api/analyze', methods=['POST', 'OPTIONS'])
def analyze_video():
    """Analyze uploaded video and return tracking results."""
    
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print(f"Received request with files: {list(request.files.keys())}")
        print(f"Received request with form data: {list(request.form.keys())}")
        
        # Check if video file is present
        if 'video' not in request.files:
            print("Error: No video file in request")
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        if file.filename == '':
            print("Error: Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"Error: Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Parse configuration
        config = {}
        if 'config' in request.form:
            try:
                config = json.loads(request.form['config'])
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid configuration format'}), 400
        
        # Save uploaded file
        filename = f"{uuid.uuid4()}_{file.filename}"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(video_path)
        
        try:
            # Run analysis
            result_csv = run_analysis(video_path, config)
            
            # Process results
            analysis_data = process_analysis_results(result_csv, video_path)
            
            if 'error' in analysis_data:
                return jsonify(analysis_data), 400
            
            # Store result metadata
            metadata = {
                'result_id': os.path.basename(result_csv).split('_')[0],
                'video_filename': filename,
                'config': config,
                'timestamp': datetime.now().isoformat(),
                'csv_path': result_csv
            }
            
            metadata_file = os.path.join(RESULTS_FOLDER, f"{metadata['result_id']}_metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            return jsonify(analysis_data)
            
        finally:
            # Clean up uploaded video
            if os.path.exists(video_path):
                os.remove(video_path)
                
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/api/download/<result_id>', methods=['GET'])
def download_results(result_id):
    """Download CSV results for a specific analysis."""
    
    csv_path = os.path.join(RESULTS_FOLDER, f"{result_id}_data.csv")
    
    if not os.path.exists(csv_path):
        return jsonify({'error': 'Results not found'}), 404
    
    return send_file(csv_path, as_attachment=True, download_name=f'analysis_{result_id}.csv')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/classes', methods=['GET'])
def get_object_classes():
    """Get available object classes for detection."""
    
    classes = [
        {'id': 32, 'name': 'sports ball', 'description': 'Sports balls (basketball, soccer, etc.)'},
        {'id': 0, 'name': 'person', 'description': 'Human person'},
        {'id': 1, 'name': 'bicycle', 'description': 'Bicycle'},
        {'id': 2, 'name': 'car', 'description': 'Automobile'},
        {'id': 39, 'name': 'bottle', 'description': 'Bottle'},
        {'id': 3, 'name': 'motorcycle', 'description': 'Motorcycle'},
        {'id': 5, 'name': 'bus', 'description': 'Bus'},
        {'id': 7, 'name': 'truck', 'description': 'Truck'},
    ]
    
    return jsonify(classes)

if __name__ == '__main__':
    print("Starting ImpulseCV Backend API...")
    print("Available endpoints:")
    print("  POST /api/analyze - Analyze uploaded video")
    print("  GET  /api/download/<result_id> - Download CSV results")
    print("  GET  /api/health - Health check")
    print("  GET  /api/classes - Get object classes")
    print("\nMake sure yolov8n.pt is in the current directory")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
