#!/usr/bin/env python3
"""
Simple Demo Script for ImpulseCV
Fallback option if web app has issues
"""

import cv2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ultralytics import YOLO
from physics_engine import PhysicsEngine
import os

def run_simple_demo():
    """Run a simple demo of ImpulseCV functionality"""
    print("🏆 ImpulseCV - Simple Demo Mode")
    print("=" * 40)
    
    # Initialize model
    print("🤖 Loading YOLO model...")
    model = YOLO('yolov8n.pt')
    print("✅ Model loaded!")
    
    # Check for video files
    video_files = []
    for file in os.listdir('./assets'):
        if file.lower().endswith(('.mp4', '.mov', '.avi')):
            video_files.append(file)
    
    if not video_files:
        print("❌ No video files found in ./assets folder")
        return
    
    print(f"📹 Found videos: {', '.join(video_files)}")
    
    # Use first video
    video_file = video_files[0]
    video_path = f'./assets/{video_file}'
    print(f"🎬 Processing: {video_file}")
    
    # Process video
    print("🔍 Processing video...")
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    data = []
    frame_idx = 0
    
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        
        frame_idx += 1
        t_sec = frame_idx / fps
        
        # Progress indicator
        if frame_idx % 10 == 0:
            progress = (frame_idx / total_frames) * 100
            print(f"   Progress: {progress:.1f}% ({frame_idx}/{total_frames} frames)")
        
        # Run tracking
        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            conf=0.15,
            iou=0.5,
            imgsz=960,
            verbose=False
        )
        
        r = results[0]
        
        # Collect data
        if r.boxes is not None and len(r.boxes):
            boxes = r.boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i])
                track_id = int(boxes.id[i]) if boxes.id is not None else -1
                conf = float(boxes.conf[i])
                x1, y1, x2, y2 = map(float, boxes.xyxy[i].tolist())
                cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
                
                data.append([
                    frame_idx, t_sec, track_id, cls_id, model.names[cls_id],
                    conf, x1, y1, x2, y2, cx, cy
                ])
    
    cap.release()
    print(f"✅ Processing complete! {len(data)} data points collected")
    
    if len(data) == 0:
        print("❌ No objects detected in video")
        return
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=[
        'frame', 'time_s', 'track_id', 'class_id', 'class_name',
        'conf', 'x1', 'y1', 'x2', 'y2', 'cx', 'cy'
    ])
    
    # Calculate physics
    print("🧮 Calculating physics metrics...")
    physics_engine = PhysicsEngine(pixels_per_meter=50.0, object_mass=0.5)
    df = physics_engine.calculate_physics_metrics(df)
    
    # Analyze trajectory
    trajectory_analysis = physics_engine.analyze_trajectory(df)
    physics_insights = physics_engine.calculate_physics_insights(df)
    
    # Display results
    print("\n📊 ANALYSIS RESULTS")
    print("=" * 40)
    print(f"📈 Data Points: {len(data)}")
    print(f"⏱️  Duration: {trajectory_analysis['duration']:.2f} seconds")
    print(f"📏 Distance: {trajectory_analysis['total_distance']:.2f} meters")
    print(f"🏃 Max Speed: {trajectory_analysis['max_speed']:.2f} m/s")
    print(f"📐 Max Height: {trajectory_analysis['max_height']:.2f} meters")
    print(f"🎯 Projectile Motion: {'Yes' if trajectory_analysis['is_projectile'] else 'No'}")
    
    print("\n🧠 PHYSICS INSIGHTS")
    print("=" * 40)
    for insight in physics_insights:
        print(f"   {insight}")
    
    # Generate plots
    print("\n📊 Generating visualizations...")
    plots = physics_engine.generate_advanced_plots(df)
    print(f"✅ Generated {len(plots)} plots:")
    for name, path in plots.items():
        print(f"   📈 {name}: {path}")
    
    # Save data
    csv_filename = f"demo_results_{video_file.replace('.', '_')}.csv"
    df.to_csv(csv_filename, index=False)
    print(f"💾 Data saved to: {csv_filename}")
    
    print("\n🎉 Demo complete!")
    print("=" * 40)
    print("🌐 For web interface, run: python app.py")
    print("📊 Check generated plots in static/plots/")
    print("📄 View data in the CSV file")

if __name__ == "__main__":
    try:
        run_simple_demo()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure you have video files in ./assets/")
        print("   2. Check that all dependencies are installed")
        print("   3. Try running: pip install -r requirements.txt")
