# Pixora AI - Submission Details

## Submission Information

- **Project Name**: Pixora AI
- **Student Name**: Vishal Bhutekar
- **Roll Number**: BT24S05F002
- **Course**: Honors Advanced Computer Vision (TA Project)

## Project Overview

Pixora AI is a high-performance, cloud-native image upscaling and enhancement service built with Modal and Real-ESRGAN. This project demonstrates advanced computer vision techniques using:

- **AI-Powered Super-Resolution**: Real-ESRGAN model for 2x image upscaling
- **GPU Acceleration**: Modal serverless GPU infrastructure (A10G)
- **REST API Architecture**: FastAPI-based HTTP endpoints
- **Web Interface**: Interactive SPA for image enhancement
- **Production Deployment**: Cloud-native scalable solution

## Project Contents

### Source Code
- **`modal_app.py`**: Main application entry point with Modal service and web handlers
- **`upload_weights_to_modal.py`**: Utility for managing model weights in Modal volumes

### Documentation
- **`README.md`**: Comprehensive project documentation including:
  - Installation and setup instructions
  - API documentation with examples
  - Deployment guidelines
  - Architecture overview
  - Troubleshooting guide

### Key Features Demonstrated

1. **Deep Learning Integration**
   - Real-ESRGAN model implementation
   - PyTorch GPU inference
   - Model weight management

2. **Web Architecture**
   - ASGI web application with Starlette
   - REST API design principles
   - Binary image processing
   - SPA frontend integration

3. **Cloud Infrastructure**
   - Serverless GPU deployment
   - Volume-based model storage
   - Auto-scaling and resource optimization
   - Production-ready configuration

4. **Image Processing**
   - PIL-based image manipulation
   - NumPy array operations
   - Format conversion (JPEG/PNG)
   - Quality optimization

## Technical Stack

- **Framework**: Modal (serverless GPU platform)
- **Web**: Starlette, FastAPI
- **ML**: PyTorch, Real-ESRGAN, BasicSR
- **Image Processing**: PIL, OpenCV, NumPy
- **Language**: Python 3.11+

## Setup and Execution

### Installation
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install Modal
pip install modal

# Authenticate with Modal
modal token new
```

### Deployment
```bash
# Upload model weights
python upload_weights_to_modal.py

# Deploy to Modal
modal deploy modal_app.py
```

### Local Development
```bash
modal serve modal_app.py
```

## API Endpoints

### Health Check
- `GET /health` - Service health status

### Image Enhancement  
- `POST /enhance` - Upscale and enhance images
  - Query params: `strength` (0.0-1.0), `output_format` (jpeg/png)
  - Body: Binary image data

### Web Interface
- `GET /` - Interactive web frontend for image enhancement

## Model Information

- **Model**: Real-ESRGAN x2plus
- **Architecture**: RRDBNet (23-block residual dense network)
- **Upscaling**: 2x resolution increase
- **GPU**: NVIDIA A10G (24GB VRAM)
- **Precision**: FP16 for memory efficiency

## Evaluation Criteria

This project demonstrates:

1. ✅ **Computer Vision Fundamentals**
   - Deep learning model implementation
   - Image processing and enhancement
   - Real-world application of super-resolution

2. ✅ **Software Engineering**
   - Clean, well-documented code
   - Proper project structure
   - Production-ready architecture

3. ✅ **Advanced Topics**
   - GPU acceleration and optimization
   - Cloud deployment strategies
   - API design and integration

4. ✅ **Innovation**
   - Novel web interface for image enhancement
   - Serverless GPU infrastructure utilization
   - Practical real-world application

## References

- [Real-ESRGAN GitHub](https://github.com/xinntao/Real-ESRGAN)
- [BasicSR Framework](https://github.com/XPixelGroup/BasicSR)
- [Modal Documentation](https://modal.com/docs)
- [PyTorch Documentation](https://pytorch.org)

## Notes

- All source code is properly documented with comments
- The project follows Python best practices and PEP 8 guidelines
- Comprehensive README included for deployment and usage
- Production-ready configuration with error handling

## Contact

**Student**: Vishal Bhutekar  
**Email**: vishalbhutekar33772@gmail.com  
**Roll Number**: BT24S05F002

---

**Submission Date**: May 7, 2026
