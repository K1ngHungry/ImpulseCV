import cv2
import numpy as np
import pandas as pd
from ultralytics import YOLO
import os
from physics_engine import PhysicsEngine

def create_tracking_video(input_video_path, output_video_path, data_csv_path):
    """
    Create a video with tracking visualization including:
    - Bounding boxes around detected objects
    - Trajectory trails
    - Force and velocity vectors
    - Frame counter and info
    """
    
    # Load the tracking data
    df = pd.read_csv(data_csv_path)
    
    # Calculate physics metrics for vector visualization
    physics_engine = PhysicsEngine(pixels_per_meter=50.0, object_mass=0.5)
    df_physics = physics_engine.calculate_physics_metrics(df.copy())
    
    # Load video
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Create video writer with H.264 codec for better browser compatibility
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    frame_idx = 0
    trajectory_points = []  # Store trajectory for drawing
    
    print(f"Creating tracking video with force and velocity vectors...")
    
    # Create extrapolation data for missing frames
    extrapolated_data = create_extrapolation_data(df_physics)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_idx += 1
        
        # Get tracking data for this frame
        frame_data = df[df['frame'] == frame_idx]
        frame_physics = df_physics[df_physics['frame'] == frame_idx]
        
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
        
        # Draw bounding boxes, labels, and vectors for detected objects
        for _, row in frame_data.iterrows():
            x1, y1, x2, y2 = int(row['x1']), int(row['y1']), int(row['x2']), int(row['y2'])
            track_id = int(row['track_id'])
            conf = row['conf']
            class_name = row['class_name']
            cx, cy = int(row['cx']), int(row['cy'])
            
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
            
            # Draw force and velocity vectors
            physics_row = frame_physics[frame_physics['track_id'] == track_id]
            if not physics_row.empty:
                physics_row = physics_row.iloc[0]
                draw_physics_vectors(frame, physics_row, cx, cy, fps)
        
        # Draw extrapolated vectors for missing frames
        if frame_idx in extrapolated_data:
            for track_id, extrap_data in extrapolated_data[frame_idx].items():
                cx, cy = extrap_data['cx'], extrap_data['cy']
                physics_row = extrap_data['physics']
                draw_physics_vectors(frame, physics_row, int(cx), int(cy), fps)
        
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
        
        # Add vector legend
        draw_vector_legend(frame, width, height)
        
        # Write frame to output video
        out.write(frame)
        
        # Show progress
        if frame_idx % 30 == 0:
            print(f"Processed {frame_idx} frames...")
    
    cap.release()
    out.release()
    print(f"Tracking video saved to: {output_video_path}")

def draw_physics_vectors(frame, physics_row, cx, cy, fps):
    """
    Draw separate force and velocity vectors on the frame
    """
    # Much larger vector scaling factors for visibility
    velocity_scale = 8.0  # pixels per m/s (4x larger)
    force_scale = 15.0    # pixels per N (150x larger for gravity)
    
    # Get physics data
    vx = physics_row.get('vx_m', 0)  # velocity x in m/s
    vy = physics_row.get('vy_m', 0)  # velocity y in m/s
    mass = 0.5  # kg (assumed mass)
    
    # Convert to pixel coordinates
    vx_px = vx * velocity_scale
    vy_px = vy * velocity_scale
    
    # Draw velocity vector (blue) - always show if there's any velocity
    if abs(vx_px) > 2 or abs(vy_px) > 2:  # Lower threshold for visibility
        v_end_x = int(cx + vx_px)
        v_end_y = int(cy + vy_px)
        draw_arrow(frame, (cx, cy), (v_end_x, v_end_y), (255, 0, 0), 4)  # Blue, thicker
        cv2.putText(frame, "v", (v_end_x + 8, v_end_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Draw gravity force vector (green) - always downward, always show
    gravity_force = 9.81 * mass  # N
    gravity_px = gravity_force * force_scale
    g_end_x = cx
    g_end_y = int(cy + gravity_px)
    draw_arrow(frame, (cx, cy), (g_end_x, g_end_y), (0, 255, 0), 4)  # Green, thicker
    cv2.putText(frame, "Fg", (g_end_x + 8, g_end_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def draw_arrow(frame, start, end, color, thickness):
    """
    Draw an arrow from start to end point
    """
    # Draw main line
    cv2.line(frame, start, end, color, thickness)
    
    # Calculate arrow head
    angle = np.arctan2(end[1] - start[1], end[0] - start[0])
    arrow_length = 15
    arrow_angle = np.pi / 6  # 30 degrees
    
    # Arrow head points
    head1 = (
        int(end[0] - arrow_length * np.cos(angle - arrow_angle)),
        int(end[1] - arrow_length * np.sin(angle - arrow_angle))
    )
    head2 = (
        int(end[0] - arrow_length * np.cos(angle + arrow_angle)),
        int(end[1] - arrow_length * np.sin(angle + arrow_angle))
    )
    
    # Draw arrow head
    cv2.line(frame, end, head1, color, thickness)
    cv2.line(frame, end, head2, color, thickness)

def create_extrapolation_data(df_physics):
    """
    Create extrapolated position and physics data for missing frames
    """
    extrapolated_data = {}
    
    # Get all unique track IDs
    track_ids = df_physics['track_id'].unique()
    
    for track_id in track_ids:
        track_data = df_physics[df_physics['track_id'] == track_id].sort_values('frame')
        
        if len(track_data) < 2:
            continue
            
        # Get frame range
        min_frame = track_data['frame'].min()
        max_frame = track_data['frame'].max()
        
        # Create interpolation for missing frames
        for frame in range(min_frame, max_frame + 1):
            if frame not in track_data['frame'].values:
                # Find the two nearest frames for interpolation
                before_frames = track_data[track_data['frame'] < frame]
                after_frames = track_data[track_data['frame'] > frame]
                
                if len(before_frames) > 0 and len(after_frames) > 0:
                    before_row = before_frames.iloc[-1]
                    after_row = after_frames.iloc[0]
                    
                    # Linear interpolation
                    t = (frame - before_row['frame']) / (after_row['frame'] - before_row['frame'])
                    
                    # Interpolate position
                    cx = before_row['cx_m'] + t * (after_row['cx_m'] - before_row['cx_m'])
                    cy = before_row['cy_m'] + t * (after_row['cy_m'] - before_row['cy_m'])
                    
                    # Interpolate velocity
                    vx = before_row['vx_m'] + t * (after_row['vx_m'] - before_row['vx_m'])
                    vy = before_row['vy_m'] + t * (after_row['vy_m'] - before_row['vy_m'])
                    
                    # Create physics row for extrapolation
                    physics_row = {
                        'vx_m': vx,
                        'vy_m': vy,
                        'cx_m': cx,
                        'cy_m': cy
                    }
                    
                    if frame not in extrapolated_data:
                        extrapolated_data[frame] = {}
                    
                    extrapolated_data[frame][track_id] = {
                        'cx': cx * 50.0,  # Convert back to pixels
                        'cy': cy * 50.0,  # Convert back to pixels
                        'physics': physics_row
                    }
    
    return extrapolated_data

def draw_vector_legend(frame, width, height):
    """
    Draw a legend explaining the vector colors
    """
    legend_x = width - 200
    legend_y = 30
    
    # Background
    cv2.rectangle(frame, (legend_x - 10, legend_y - 10), 
                 (legend_x + 190, legend_y + 100), (0, 0, 0), -1)
    cv2.rectangle(frame, (legend_x - 10, legend_y - 10), 
                 (legend_x + 190, legend_y + 100), (255, 255, 255), 2)
    
    # Title
    cv2.putText(frame, "Vectors:", (legend_x, legend_y + 15), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Velocity vector
    cv2.putText(frame, "Blue: Velocity", (legend_x, legend_y + 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Gravity force
    cv2.putText(frame, "Green: Gravity", (legend_x, legend_y + 55), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
    
    # Tracking parameters - more permissive for better detection
    tracker_cfg = "bytetrack.yaml"
    CONF = 0.1  # Lower confidence threshold
    IOU = 0.7   # Higher IoU for better tracking
    IMGZ = 640  # Smaller image size for faster processing
    
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
        
        # Run tracking with multiple object classes
        target_classes = [TARGET] if TARGET is not None else [0, 1, 2, 3, 4, 5]  # Include common objects
        
        results = model.track(
            frame,
            persist=True,
            tracker=tracker_cfg,
            conf=CONF,
            iou=IOU,
            imgsz=IMGZ,
            classes=target_classes,
            verbose=False
        )
        
        r = results[0]
        
        # Collect tracking data - collect all detected objects
        if r.boxes is not None and len(r.boxes):
            boxes = r.boxes
            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i])
                # Collect all objects, not just sports ball
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
