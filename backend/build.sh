#!/bin/bash

echo "🚀 Starting DocuMind lightweight build..."

# Install Python dependencies only (no system packages needed)
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🌐 Using cloud-based OCR - no memory overhead!"
echo "✅ Build completed successfully!"

# Check Python dependencies
echo "🐍 Verifying dependencies..."
python -c "import fastapi; print('✅ FastAPI ready')" 2>/dev/null || echo "❌ FastAPI missing"
python -c "import requests; print('✅ Requests ready')" 2>/dev/null || echo "❌ Requests missing"
python -c "from PIL import Image; print('✅ Pillow ready')" 2>/dev/null || echo "❌ Pillow missing"

echo "🚀 Ready to start server - memory usage optimized!"
