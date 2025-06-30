#!/bin/bash

# Update package list
apt-get update

# Install system dependencies for PDF and image processing
apt-get install -y tesseract-ocr tesseract-ocr-eng
apt-get install -y poppler-utils
apt-get install -y libgl1-mesa-glx
apt-get install -y libglib2.0-0

# Verify installations
tesseract --version
pdftoppm -h

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "Build completed successfully!"
