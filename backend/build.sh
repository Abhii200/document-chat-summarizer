#!/bin/bash

echo "🚀 Starting DocuMind backend build..."

# Install Python dependencies first
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔍 Checking system dependencies..."

# Check for system dependencies and install if possible
if command -v apt-get &> /dev/null; then
    echo "📋 Attempting to install system dependencies..."
    
    # Try to install with error handling
    apt-get update 2>/dev/null || echo "⚠️ Could not update package list"
    apt-get install -y tesseract-ocr 2>/dev/null || echo "⚠️ Could not install tesseract via apt"
    apt-get install -y poppler-utils 2>/dev/null || echo "⚠️ Could not install poppler-utils via apt"
else
    echo "📋 apt-get not available, skipping system package installation"
fi

# Verify what's available
echo "🔍 Checking available tools..."

if command -v tesseract &> /dev/null; then
    echo "✅ Tesseract is available"
    tesseract --version 2>/dev/null || echo "⚠️ Tesseract version check failed"
else
    echo "⚠️ Tesseract not found - will use EasyOCR fallback"
fi

if command -v pdftoppm &> /dev/null; then
    echo "✅ pdftoppm is available"
else
    echo "⚠️ pdftoppm not found - PDF processing may be limited"
fi

# Check Python dependencies
echo "🐍 Verifying Python dependencies..."
python -c "import fastapi; print('✅ FastAPI available')" 2>/dev/null || echo "❌ FastAPI not available"
python -c "import easyocr; print('✅ EasyOCR available')" 2>/dev/null || echo "⚠️ EasyOCR not available"
python -c "import pytesseract; print('✅ pytesseract available')" 2>/dev/null || echo "⚠️ pytesseract not available"

echo "✅ Build process completed!"
echo "🚀 Starting server..."
