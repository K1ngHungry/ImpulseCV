# ImpulseCV - Physics Learning Tool for Object Tracking

A physics education tool designed to help students visualize motion concepts through video analysis. The tool uses computer vision to track objects in videos and extract position data for physics analysis.

## Current Features

- **Object Detection**: Uses YOLOv8 for robust object detection
- **Object Tracking**: Implements ByteTrack for consistent object tracking across frames
- **Data Export**: Export tracking results to CSV format with frame-by-frame position data
- **Video Processing**: Processes video files frame by frame for analysis
- **Configurable Detection**: Adjustable confidence thresholds and object class filtering

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

### Basic Workflow

1. **Configure Detection**: Edit `main.py` to set parameters:
   - `CONF`: Confidence threshold (default: 0.15)
   - `TARGET`: Object class ID to track (default: sports ball = 32)
   - `video_path`: Path to video file (default: './ball-in.mp4')
2. **Run Analysis**: Execute the script to process the video
3. **View Results**: Check `data.csv` for tracking results
4. **Analyze Data**: Use the exported CSV data for further physics analysis

### Current Configuration

The script is currently configured to:
- Track sports balls (class ID 32) in `ball-in.mp4`
- Use confidence threshold of 0.15
- Process at 960px input resolution
- Export data to `data.csv`

### Object Classes (COCO Dataset)

- 0: person
- 1: bicycle
- 2: car
- 3: motorcycle
- 4: airplane
- 5: bus
- 6: train
- 7: truck
- 8: boat
- 9: traffic light
- ... (and more)

## Technical Details

### Detection Pipeline

1. **YOLOv8 Detection**: 
   - Uses YOLOv8n.pt (nano) model for speed
   - Configurable confidence and IoU thresholds
   - Class-specific filtering

2. **ByteTrack Tracking**:
   - Maintains consistent object IDs across frames
   - Uses ByteTrack algorithm for robust tracking
   - Handles object persistence across frames

### Current Data Output

The script outputs tracking data with the following information:
1. **Frame Information**: Frame number and timestamp
2. **Object Data**: Track ID, class ID, class name, confidence score
3. **Position Data**: Bounding box coordinates (x1, y1, x2, y2) and centroid (cx, cy)

### Planned Trajectory Processing

1. **Gap Filling**: Linear interpolation for gaps up to 5 frames
2. **Smoothing**: Savitzky-Golay filter with adaptive window size
3. **Vector Computation**:
   - Velocity: Central difference of position
   - Acceleration: Central difference of velocity
   - Momentum: mass × velocity (if mass provided)
   - Force: mass × acceleration (if mass provided)

### Current CSV Output Schema

The exported CSV contains the following columns:

- `frame`: Frame number
- `time_s`: Time in seconds
- `track_id`: Object tracking ID
- `class_id`: Object class ID (32 for sports ball)
- `class_name`: Object class name
- `conf`: Detection confidence score
- `x1`, `y1`, `x2`, `y2`: Bounding box coordinates in pixels
- `cx`, `cy`: Centroid position in pixels

### Planned Enhanced CSV Output

Future versions will include:
- `vx`, `vy`: Velocity components in pixels/second
- `ax`, `ay`: Acceleration components in pixels/second²
- `tracked_bool`: Whether object was tracked in this frame
- `cx_px_smooth`, `cy_px_smooth`: Smoothed position data
- `cx_m`, `cy_m`: Position in meters (if pixels_per_meter provided)
- `vx_m`, `vy_m`: Velocity in m/s (if pixels_per_meter provided)
- `ax_m`, `ay_m`: Acceleration in m/s² (if pixels_per_meter provided)
- `px`, `py`: Momentum components (if mass provided)
- `Fx`, `Fy`: Force components (if mass provided)

## Educational Applications

### Physics Concepts Demonstrated

1. **Projectile Motion**: Analyze the parabolic trajectory of thrown objects
2. **Force Diagrams**: Visualize net forces acting on objects
3. **Momentum Conservation**: Track momentum changes in collisions
4. **Acceleration Analysis**: Study acceleration patterns in different motions
5. **Energy Concepts**: Relate velocity changes to kinetic energy

### Classroom Use

- Upload videos of physics demonstrations
- Compare theoretical predictions with real-world measurements
- Generate force diagrams from actual motion data
- Analyze the effects of air resistance and other forces
- Study the relationship between position, velocity, and acceleration

## Tips for Best Results

1. **Video Quality**: Use high-resolution videos with good lighting
2. **Object Visibility**: Ensure the target object is clearly visible throughout the video
3. **Camera Stability**: Minimize camera shake for more accurate tracking
4. **Background**: Simple backgrounds work better than cluttered scenes
5. **Object Size**: Objects should be large enough to be detected reliably
6. **Calibration**: Use known distances to set accurate pixels_per_meter values

## Troubleshooting

### Common Issues

1. **Poor Tracking**: 
   - Lower confidence threshold
   - Check object visibility
   - Try different object classes

2. **Inaccurate Vectors**:
   - Ensure stable camera
   - Check pixels_per_meter calibration
   - Verify mass values

3. **Performance Issues**:
   - Use shorter video clips
   - Lower video resolution
   - Close other applications

## Dependencies

### Currently Used
- ultralytics: YOLOv8 object detection and ByteTrack tracking
- opencv-python: Video processing and visualization
- numpy: Numerical computations (installed with ultralytics)

### Planned Dependencies
- scipy: Signal processing and filtering
- pandas: Data manipulation
- matplotlib: Plotting and visualization
- tkinter: GUI framework (included with Python)
- Pillow: Image processing

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Future Enhancements

- Support for multiple object tracking
- Real-time analysis capabilities
- Advanced physics simulations
- Integration with physics education platforms
- Mobile app version
- Cloud-based processing
