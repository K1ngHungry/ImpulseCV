# ImpulseCV - AI Object Tracking & Physics Analysis

A modern web application that combines computer vision, object tracking, and physics analysis to provide comprehensive motion analysis from video input.

## 🚀 Features

- **AI Object Detection**: YOLOv8-powered real-time object detection
- **Object Tracking**: ByteTrack algorithm for consistent multi-object tracking
- **Physics Analysis**: Advanced motion analysis including velocity, acceleration, energy, and trajectory
- **Modern UI**: React frontend with Tailwind CSS for a professional interface
- **Video Visualization**: Real-time tracking with bounding boxes and trajectory overlay
- **Data Export**: CSV export of all tracking data and physics calculations

## 🏗️ Architecture

### Frontend (React + Tailwind CSS)
- **Location**: `/frontend/`
- **Port**: `http://localhost:5173`
- **Tech Stack**: React 18, Vite, Tailwind CSS, Modern JavaScript

### Backend (Flask API)
- **Location**: `/backend/`
- **Port**: `http://localhost:8000`
- **Tech Stack**: Flask, OpenCV, YOLOv8, Pandas, NumPy, SciPy

## 🛠️ Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 18+ with npm
- Git

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd ImpulseCV
```

### 2. Start Backend API
```bash
chmod +x start_backend.sh
./start_backend.sh
```
The backend will be available at `http://localhost:8000`

### 3. Start Frontend (New Terminal)
```bash
chmod +x start_frontend.sh
./start_frontend.sh
```
The frontend will be available at `http://localhost:5173`

## 📁 Project Structure

```
ImpulseCV/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx         # Main app component
│   │   └── index.css       # Tailwind CSS
│   ├── package.json        # Frontend dependencies
│   └── vite.config.js      # Vite configuration
├── backend/                 # Flask API backend
│   ├── app.py              # Main Flask application
│   ├── physics_engine.py   # Physics calculations
│   ├── tracking_video_generator.py
│   ├── requirements.txt    # Python dependencies
│   └── assets/             # Video files
├── start_backend.sh        # Backend startup script
├── start_frontend.sh       # Frontend startup script
└── README.md              # This file
```

## 🎯 Usage

1. **Upload Video**: Drag & drop a video file or select from sample videos
2. **AI Processing**: The system automatically detects and tracks objects
3. **View Results**: See real-time tracking visualization and physics analysis
4. **Download Data**: Export CSV files with complete motion data

## 🔧 API Endpoints

### Core Endpoints
- `GET /` - API health check
- `GET /status` - Processing status
- `GET /assets` - List available videos
- `POST /upload` - Upload new video
- `GET /process_asset/<filename>` - Process video
- `GET /download/<filename>` - Download CSV data
- `GET /videos/<filename>` - Serve tracking videos
- `GET /plots/<filename>` - Serve analysis plots

## 🎨 Frontend Components

- **Header**: Navigation and branding
- **VideoUpload**: Drag & drop file upload with sample videos
- **ProcessingStatus**: Real-time progress tracking
- **TrackingVideo**: Video player with AI tracking overlay
- **AnalysisResults**: Physics analysis and data export

## 🔬 Physics Analysis

The system calculates:
- **Kinematics**: Position, velocity, acceleration
- **Dynamics**: Force, momentum, energy
- **Trajectory**: Path analysis and smoothing
- **Statistics**: Max/min values, averages, trends

## 🚀 Deployment

### Development
- Backend: `python backend/app.py`
- Frontend: `npm run dev` in `/frontend/`

### Production
- Backend: Use Gunicorn or similar WSGI server
- Frontend: Build with `npm run build` and serve static files

## 📊 Sample Videos

The system includes sample videos for testing:
- `ball-in.mp4` - Ball motion analysis
- `teddy.mp4` - Object tracking demo

## 🎓 Educational Applications

Perfect for:
- Physics education and motion analysis
- Computer vision learning
- Data visualization projects
- Hackathon demonstrations
- Research and prototyping

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- ByteTrack for object tracking
- OpenCV for computer vision
- React and Tailwind CSS for modern UI
