#!/bin/bash
# ImpulseCV Startup Script

echo "🏆 Starting ImpulseCV - Hackathon Winning Physics Education Platform"
echo "================================================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ app.py not found. Please run this script from the ImpulseCV directory"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
python3 -m pip install -r requirements.txt --quiet

# Start the application
echo "🚀 Starting ImpulseCV web application..."
echo "🌐 Open your browser to: http://localhost:5000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python3 app.py
