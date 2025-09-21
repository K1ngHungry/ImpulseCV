#!/bin/bash

echo "🎨 Starting ImpulseCV React Frontend..."
echo "📁 Frontend directory: $(pwd)/frontend"
echo "📦 Node modules: Installing..."

cd frontend

# Install Node.js dependencies
npm install

echo "✅ Frontend setup complete!"
echo "🌐 Starting React development server on http://localhost:5173"
echo "🎯 Make sure the backend API is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"

npm run dev
