#!/bin/bash

# Install system dependencies for Render
apt-get update
apt-get install -y tesseract-ocr
apt-get install -y poppler-utils

# Install Python dependencies
pip install -r requirements.txt
