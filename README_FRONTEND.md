# ImpulseCV Frontend

A modern React/TypeScript frontend for the ImpulseCV physics learning tool, providing an intuitive interface for video analysis and trajectory visualization.

## Features

- **Video Upload**: Drag-and-drop interface for video files
- **Analysis Configuration**: Adjustable detection parameters
- **Real-time Visualization**: Interactive trajectory charts
- **Statistics Dashboard**: Comprehensive analysis metrics
- **Data Export**: Download results as CSV files

## Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **React Dropzone** for file uploads
- **Lucide React** for icons

## Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### 3. Start Backend API

In a separate terminal:

```bash
# Install backend dependencies
pip install -r requirements_backend.txt

# Start the Flask API
python backend_api.py
```

The API will be available at `http://localhost:5000`

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.tsx           # App header
│   │   ├── VideoUpload.tsx      # File upload component
│   │   ├── AnalysisConfig.tsx   # Analysis settings
│   │   ├── AnalysisResults.tsx  # Results display
│   │   ├── TrajectoryChart.tsx  # Trajectory visualization
│   │   └── StatisticsPanel.tsx  # Statistics dashboard
│   ├── types/
│   │   └── index.ts            # TypeScript definitions
│   ├── App.tsx                 # Main app component
│   ├── index.tsx              # App entry point
│   └── index.css              # Global styles
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

## API Integration

The frontend communicates with the Python backend via REST API:

### Endpoints

- `POST /api/analyze` - Upload video and start analysis
- `GET /api/download/<result_id>` - Download CSV results
- `GET /api/health` - Health check
- `GET /api/classes` - Get available object classes

### Request Format

```typescript
// Analysis request
const formData = new FormData();
formData.append('video', videoFile);
formData.append('config', JSON.stringify({
  confidence: 0.15,
  objectClass: 32,
  inputSize: 960,
  iouThreshold: 0.5
}));
```

### Response Format

```typescript
interface AnalysisData {
  frames: number;
  duration: number;
  fps: number;
  trajectory: TrajectoryPoint[];
  statistics: AnalysisStatistics;
  trackIds: number[];
  confidence: ConfidenceStats;
}
```

## Configuration Options

### Detection Parameters

- **Confidence Threshold**: 0.1 - 1.0 (default: 0.15)
- **Object Class**: Sports ball, person, bicycle, car, etc.
- **Input Size**: 640px - 1280px (default: 960px)
- **IoU Threshold**: 0.1 - 1.0 (default: 0.5)

### Optional Settings

- **Pixels per Meter**: For real-world scaling
- **Object Mass**: For physics calculations

## Visualization Features

### Trajectory Chart

- Interactive scatter plot showing ball position over time
- Color-coded by frame number
- Hover tooltips with detailed information
- Reference lines for position context

### Statistics Dashboard

- **Motion Metrics**: Duration, frames, FPS
- **Velocity Analysis**: Max and average velocity
- **Position Range**: X and Y coordinate bounds
- **Confidence Stats**: Detection quality metrics
- **Tracking Info**: Track IDs and consistency

## Development

### Adding New Components

1. Create component in `src/components/`
2. Add TypeScript interfaces in `src/types/`
3. Import and use in `App.tsx`

### Styling Guidelines

- Use Tailwind CSS utility classes
- Follow the design system in `index.css`
- Use semantic color names (primary, secondary)
- Maintain responsive design principles

### API Integration

- All API calls go through the proxy to `localhost:5000`
- Use proper error handling and loading states
- Implement optimistic updates where appropriate

## Build and Deploy

### Production Build

```bash
npm run build
```

### Deployment

The built files in `build/` can be served by any static file server:

```bash
# Serve with Python
cd build && python -m http.server 8000

# Serve with Node.js
npx serve build
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance Considerations

- Video files are processed on the backend
- Frontend handles visualization and interaction only
- Large datasets use pagination and virtualization
- Charts are optimized for smooth rendering
