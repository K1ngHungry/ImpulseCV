#!/usr/bin/env python3
"""
Demo script to show the tracking video feature
"""

import os
import webbrowser
from flask import Flask, render_template_string

# Simple Flask app to demo the tracking video
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ImpulseCV - AI Object Tracking Demo</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-light">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-lg-10">
                <div class="text-center mb-5">
                    <h1 class="display-4 fw-bold text-primary">
                        <i class="fas fa-robot me-3"></i>ImpulseCV
                    </h1>
                    <p class="lead text-muted">AI-Powered Object Tracking & Physics Analysis</p>
                </div>

                <!-- Tracking Video Section -->
                <div class="card shadow-lg mb-5">
                    <div class="card-header bg-primary text-white">
                        <h3 class="mb-0">
                            <i class="fas fa-video me-2"></i>
                            AI Object Tracking Visualization
                        </h3>
                    </div>
                    <div class="card-body text-center">
                        <div class="mb-3">
                            <video controls class="img-fluid rounded shadow" style="max-width: 100%; height: auto;">
                                <source src="/videos/tracked_ball-in.mp4" type="video/mp4">
                                Your browser does not support the video tag.
                            </video>
                        </div>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Watch the Magic:</strong> This video shows our AI tracking a moving ball with:
                            <ul class="list-unstyled mt-2">
                                <li><i class="fas fa-square me-1 text-danger"></i> <strong>Bounding boxes</strong> around detected objects</li>
                                <li><i class="fas fa-route me-1 text-primary"></i> <strong>Trajectory trails</strong> showing movement paths</li>
                                <li><i class="fas fa-tag me-1 text-success"></i> <strong>Track IDs</strong> for consistent object following</li>
                                <li><i class="fas fa-chart-line me-1 text-warning"></i> <strong>Real-time confidence scores</strong></li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Features Section -->
                <div class="row g-4">
                    <div class="col-md-4">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body text-center">
                                <div class="feature-icon bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                                    <i class="fas fa-eye fa-lg"></i>
                                </div>
                                <h5>Computer Vision</h5>
                                <p class="text-muted">Advanced YOLOv8 + ByteTrack for precise object detection and tracking</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body text-center">
                                <div class="feature-icon bg-success text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                                    <i class="fas fa-calculator fa-lg"></i>
                                </div>
                                <h5>Physics Analysis</h5>
                                <p class="text-muted">Automatic velocity, acceleration, force, and energy calculations</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card h-100 border-0 shadow-sm">
                            <div class="card-body text-center">
                                <div class="feature-icon bg-warning text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 60px; height: 60px;">
                                    <i class="fas fa-chart-bar fa-lg"></i>
                                </div>
                                <h5>Data Visualization</h5>
                                <p class="text-muted">Interactive plots and comprehensive motion analysis</p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Results Preview -->
                <div class="card shadow-lg mt-5">
                    <div class="card-header">
                        <h4 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>
                            Analysis Results Preview
                        </h4>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Motion Metrics</h6>
                                <ul class="list-unstyled">
                                    <li><strong>Max Speed:</strong> 2058.6 m/s</li>
                                    <li><strong>Max Height:</strong> 20.8m</li>
                                    <li><strong>Duration:</strong> 1.89s</li>
                                    <li><strong>Total Distance:</strong> 7475.7m</li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6>Physics Insights</h6>
                                <ul class="list-unstyled">
                                    <li><i class="fas fa-exclamation-triangle text-warning me-1"></i> Significant energy loss detected</li>
                                    <li><i class="fas fa-rocket text-primary me-1"></i> Above-average acceleration</li>
                                    <li><i class="fas fa-running text-success me-1"></i> High-speed motion analyzed</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Call to Action -->
                <div class="text-center mt-5">
                    <a href="http://localhost:8000" class="btn btn-primary btn-lg me-3">
                        <i class="fas fa-play me-2"></i>Try Full Demo
                    </a>
                    <a href="/videos/tracked_ball-in.mp4" class="btn btn-outline-primary btn-lg" download>
                        <i class="fas fa-download me-2"></i>Download Video
                    </a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def demo():
    return render_template_string(HTML_TEMPLATE)

@app.route('/videos/<filename>')
def serve_video(filename):
    """Serve tracking videos"""
    from flask import send_file
    video_path = os.path.join('static', 'videos', filename)
    if os.path.exists(video_path):
        return send_file(video_path)
    else:
        return "Video not found", 404

if __name__ == '__main__':
    print("🎥 Starting ImpulseCV Tracking Video Demo...")
    print("📍 Demo will be available at: http://localhost:8001")
    print("🚀 Opening browser...")
    
    # Open browser after a short delay
    import threading
    import time
    
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:8001')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    app.run(debug=True, host='0.0.0.0', port=8001)
