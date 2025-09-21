import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
import os

def create_tracking_video(input_video_path, output_video_path, data_csv_path):
    """
    Create a video with tracking visualization including:
    - Bounding boxes around detected objects
    - Trajectory trails
    - Frame counter and info
    """
    
    # Load the tracking data
    df = pd.read_csv(data_csv_path)
    
    # Load video
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    frame_idx = 0
    trajectory_points = []  # Store trajectory for drawing
    
    print(f"Creating tracking video...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_idx += 1
        
        # Get tracking data for this frame
        frame_data = df[df['frame'] == frame_idx]
        
        # Draw trajectory trail (last 30 frames)
        if len(trajectory_points) > 30:
            trajectory_points = trajectory_points[-30:]
        
        # Add current detections to trajectory
        for _, row in frame_data.iterrows():
            cx, cy = row['cx'], row['cy']
            trajectory_points.append((int(cx), int(cy), int(row['track_id'])))
        
        # Draw trajectory trails
        for i in range(len(trajectory_points) - 1):
            pt1 = trajectory_points[i]
            pt2 = trajectory_points[i + 1]
            
            # Only draw if same track ID
            if pt1[2] == pt2[2]:
                # Color based on track ID
                color = get_track_color(pt1[2])
                alpha = 0.3 + 0.7 * (i / len(trajectory_points))  # Fade effect
                cv2.line(frame, (pt1[0], pt1[1]), (pt2[0], pt2[1]), color, 2)
        
        # Draw bounding boxes and labels
        for _, row in frame_data.iterrows():
            x1, y1, x2, y2 = int(row['x1']), int(row['y1']), int(row['x2']), int(row['y2'])
            track_id = int(row['track_id'])
            conf = row['conf']
            class_name = row['class_name']
            
            # Get color for this track
            color = get_track_color(track_id)
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"ID:{track_id} {class_name} {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Add frame info overlay
        info_text = f"Frame: {frame_idx} | Time: {frame_idx/fps:.2f}s"
        cv2.putText(frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        
        # Add tracking count
        track_count = len(frame_data)
        count_text = f"Objects: {track_count}"
        cv2.putText(frame, count_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, count_text, (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
        
        # Write frame to output video
        out.write(frame)
        
        # Show progress
        if frame_idx % 30 == 0:
            print(f"Processed {frame_idx} frames...")
    
    cap.release()
    out.release()
    print(f"Tracking video saved to: {output_video_path}")

def get_track_color(track_id):
    """Generate consistent colors for track IDs"""
    colors = [
        (255, 0, 0),    # Red
        (0, 255, 0),    # Green
        (0, 0, 255),    # Blue
        (255, 255, 0),  # Cyan
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Yellow
        (128, 0, 128),  # Purple
        (255, 165, 0),  # Orange
        (0, 128, 0),    # Dark Green
        (128, 128, 0),  # Olive
    ]
    return colors[track_id % len(colors)]

def process_video_with_tracking(input_video_path, output_dir="static/videos"):
    """
    Complete pipeline: track objects and create visualization video
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load YOLO model
    model = YOLO('yolov8n.pt')
    name_to_id = {v: k for k, v in model.names.items()}
    TARGET = name_to_id.get("sports ball")
    
    print(f"Processing video: {input_video_path}")
    print(f"Target class: sports ball (ID: {TARGET})")
    
    # Setup video capture
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video: {input_video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    
    # Tracking parameters
    tracker_cfg = "bytetrack.yaml"
    CONF = 0.15
    IOU = 0.5
    IMGZ = 960
    
    # Data collection
    data = []
    frame_idx = 0
    
    print("Starting object tracking...")
    
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
            tracker=tracker_cfg,
            conf=CONF,
            iou=IOU,
            imgsz=IMGZ,
            classes=[TARGET] if TARGET is not None else None,
            verbose=False
        )
        
        r = results[0]
        
        # Collect tracking data
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
                    frame_idx, t_sec, track_id, cls_id, model.names[cls_id],
                    conf, x1, y1, x2, y2, cx, cy
                ])
        
        # Progress update
        if frame_idx % 30 == 0:
            print(f"Tracked {frame_idx} frames, {len(data)} detections")
    
    cap.release()
    
    if not data:
        raise ValueError("No objects detected in video")
    
    # Save tracking data
    csv_path = os.path.join(output_dir, "tracking_data.csv")
    df = pd.DataFrame(data, columns=[
        'frame', 'time_s', 'track_id', 'class_id', 'class_name', 'conf',
        'x1', 'y1', 'x2', 'y2', 'cx', 'cy'
    ])
    df.to_csv(csv_path, index=False)
    
    # Create tracking video
    video_name = os.path.basename(input_video_path)
    output_video_path = os.path.join(output_dir, f"tracked_{video_name}")
    
    create_tracking_video(input_video_path, output_video_path, csv_path)
    
    print(f"✅ Tracking complete!")
    print(f"📊 {len(data)} detections saved to: {csv_path}")
    print(f"🎥 Tracking video saved to: {output_video_path}")
    
    return csv_path, output_video_path

if __name__ == "__main__":
    # Test with ball-in.mp4
    input_video = "./assets/ball-in.mp4"
    if os.path.exists(input_video):
        csv_path, video_path = process_video_with_tracking(input_video)
    else:
        print(f"Video not found: {input_video}")
