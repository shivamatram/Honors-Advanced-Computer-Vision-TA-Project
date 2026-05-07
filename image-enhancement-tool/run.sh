#!/bin/bash
# QUICK START GUIDE
# Run this script to set up and start the application

echo "🖼️  Image Enhancement Toolkit - Quick Start"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""

# Activate virtual environment
echo "🚀 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

echo ""

# Create sample image
if [ ! -f "sample_images/sample.jpg" ]; then
    echo "🎨 Generating sample image..."
    python create_sample.py
    echo "✓ Sample image created"
else
    echo "✓ Sample image already exists"
fi

echo ""
echo "=========================================="
echo "✨ Setup complete! Starting application..."
echo "=========================================="
echo ""
echo "The app will open at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Run the app
streamlit run app.py
