#!/usr/bin/env python3
"""
Deployment script for ImpulseCV
Sets up the application for production deployment
"""

import os
import subprocess
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'ultralytics', 'opencv-python', 'flask', 'pandas', 
        'matplotlib', 'numpy', 'scipy', 'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ All dependencies installed!")
    else:
        print("✅ All dependencies already installed!")

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        'uploads', 'static/plots', 'templates', 
        'static/css', 'static/js', 'assets'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created/verified: {directory}")

def download_yolo_model():
    """Download YOLO model if not present"""
    print("\n🤖 Checking YOLO model...")
    
    if not os.path.exists('yolov8n.pt'):
        print("📥 Downloading YOLO model...")
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✅ YOLO model downloaded!")
    else:
        print("✅ YOLO model already present!")

def create_startup_script():
    """Create startup script for easy deployment"""
    print("\n🚀 Creating startup script...")
    
    startup_script = """#!/bin/bash
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
"""
    
    with open('start.sh', 'w') as f:
        f.write(startup_script)
    
    # Make executable
    os.chmod('start.sh', 0o755)
    print("✅ Startup script created: ./start.sh")

def create_production_config():
    """Create production configuration"""
    print("\n⚙️ Creating production configuration...")
    
    config_content = """# Production Configuration for ImpulseCV

# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Security
SECRET_KEY=your-secret-key-here

# File Upload
MAX_CONTENT_LENGTH=100MB
UPLOAD_FOLDER=uploads

# Physics Engine Defaults
DEFAULT_PIXELS_PER_METER=50.0
DEFAULT_OBJECT_MASS=0.5
DEFAULT_GRAVITY=9.81

# Processing
MAX_WORKERS=4
TIMEOUT_SECONDS=300
"""
    
    with open('.env', 'w') as f:
        f.write(config_content)
    
    print("✅ Production configuration created: .env")

def run_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        from ultralytics import YOLO
        import cv2
        import pandas as pd
        import matplotlib.pyplot as plt
        from physics_engine import PhysicsEngine
        
        print("✅ All imports successful")
        
        # Test physics engine
        engine = PhysicsEngine()
        print("✅ Physics engine initialized")
        
        # Test Flask app
        from app import app
        print("✅ Flask app loaded")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🏆 ImpulseCV Deployment Script")
    print("==============================")
    print("Setting up your hackathon-winning physics education platform...")
    
    try:
        check_dependencies()
        setup_directories()
        download_yolo_model()
        create_startup_script()
        create_production_config()
        
        if run_tests():
            print("\n🎉 Deployment successful!")
            print("\n🚀 To start the application:")
            print("   ./start.sh")
            print("\n🌐 Or manually:")
            print("   python3 app.py")
            print("\n🏆 Your hackathon-winning project is ready!")
        else:
            print("\n❌ Deployment failed. Please check the errors above.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Deployment error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
