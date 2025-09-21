#!/bin/bash

echo "🚀 Starting ImpulseCV Backend API..."
echo "📁 Backend directory: $(pwd)/backend"
echo "🐍 Python requirements: Installing..."

cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p assets static/videos static/plots

echo "✅ Backend setup complete!"
echo "🌐 Starting Flask API server on http://localhost:8000"
echo "📡 CORS enabled for React frontend"
echo ""
echo "Press Ctrl+C to stop the server"

python app.py
