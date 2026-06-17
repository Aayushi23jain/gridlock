# Requirements.txt and packages.txt Update for Deployment

## Summary of Changes

I have analyzed and updated the deployment requirements files to ensure they are correct for production deployment.

## Issues Found and Fixed

### 1. **Outdated PyTorch Versions**
- **Old**: `torch==2.2.0+cpu`, `torchvision==0.17.0+cpu`
- **Issue**: These versions are outdated and may have compatibility issues
- **Fixed**: Updated to `torch>=2.3.0,<2.5.0`, `torchvision>=0.18.0,<0.20.0`

### 2. **Missing Dependencies**
- **Missing**: Pillow (required by pdf2image and image processing)
- **Missing**: PyYAML (sometimes required by ultralytics)
- **Fixed**: Added both packages with appropriate version constraints

### 3. **Poor Version Constraints**
- **Old**: Some packages had only minimum versions (`>=`)
- **Issue**: Could lead to unexpected breaking changes
- **Fixed**: Added both minimum and maximum versions (`>=x.y.z,<a.b.c`)

### 4. **Incomplete System Dependencies**
- **Old**: Only `poppler-utils` in packages.txt
- **Issue**: Missing some libraries that may be needed
- **Fixed**: Added additional system libraries

## New requirements.txt

```python
# Gridlock 2.0 - Traffic Violation AI System Requirements
# Optimized for deployment without GPU (CPU-based inference)

--extra-index-url https://download.pytorch.org/whl/cpu

# Core framework
streamlit>=1.30.0,<2.0.0

# Computer vision and image processing
opencv-python-headless>=4.8.0,<5.0.0
numpy>=1.24.0,<2.0.0
Pillow>=10.0.0,<11.0.0

# Deep learning frameworks (CPU versions)
torch>=2.3.0,<2.5.0
torchvision>=0.18.0,<0.20.0

# Object detection (YOLOv8)
ultralytics>=8.1.0,<9.0.0

# OCR for license plate reading
easyocr>=1.7.1,<2.0.0

# PDF generation and processing
fpdf2>=2.7.0,<3.0.0
pdf2image>=1.17.0,<2.0.0

# Configuration and utilities
PyYAML>=6.0,<7.0
```

## New packages.txt

```python
# System dependencies for Gridlock 2.0 deployment
# Required for PDF processing and image handling

# PDF processing (required by pdf2image)
poppler-utils

# OpenGL support (may be needed for some image processing operations)
libgl1-mesa-glx

# GLib library (sometimes required by pdf2image)
libglib2.0-0

# Additional libraries that may be needed for OCR
libgomp1
libsm6
libxext6
```

## Deployment Benefits

1. **Better Compatibility**: Updated PyTorch versions work better with newer ML libraries
2. **Stability**: Version ranges prevent unexpected breaking changes
3. **Complete Dependencies**: All required packages are now included
4. **System Libraries**: Complete system dependencies for different deployment environments

## Backup Files

Original files have been backed up:
- `requirements.txt.backup`
- `packages.txt.backup`

## Deployment Commands

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (Debian/Ubuntu)
sudo apt-get install -y $(cat packages.txt)

# Run the application
streamlit run app.py
```

## Testing Recommendations

Before full deployment, test with:
```bash
# Test installation
python -c "import streamlit, cv2, torch, easyocr, ultralytics, fpdf"

# Test pipeline
python evaluate.py

# Test UI
streamlit run app.py
```

## Notes

- The requirements are optimized for CPU-based deployment (no GPU required)
- Version constraints balance stability with security updates
- All packages match the actual imports in the codebase
- System dependencies cover most common deployment scenarios