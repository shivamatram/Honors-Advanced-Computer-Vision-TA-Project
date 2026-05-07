# Pixora AI - Real-ESRGAN Image Enhancement Service

A high-performance, cloud-native image upscaling and enhancement service built with Modal and Real-ESRGAN. Enhance low-resolution images with state-of-the-art AI-powered super-resolution on GPU infrastructure.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **AI-Powered Image Upscaling**: Uses Real-ESRGAN (2x upscaling) for high-quality image enhancement
- **GPU-Accelerated Inference**: Runs on Modal's A10G GPUs for fast processing
- **REST API**: Simple HTTP POST endpoints for image enhancement
- **Flexible Output Formats**: Support for JPEG and PNG output
- **Strength Control**: Adjustable blend factor (0.0-1.0) to control enhancement intensity
- **Scalable Architecture**: Auto-scaling with Modal's serverless infrastructure
- **Web Frontend**: Integrated SPA for interactive image upload and preview
- **Production-Ready**: Optimized for low-latency batch processing

## 🏗️ Architecture

```
┌─────────────────────┐
│   Web Frontend      │ (SPA - React/Vue)
│   (index.html)      │
└──────────┬──────────┘
           │
┌──────────▼──────────────────────────────┐
│    Modal ASGI Web App                   │
│  ┌──────────────────────────────────┐   │
│  │ /health           → Health Check │   │
│  │ /enhance          → Image Process│   │
│  │ /{path}           → SPA Fallback │   │
│  └──────────────────────────────────┘   │
└──────────┬──────────────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│  GPU Inference Service (A10G)           │
│  ┌──────────────────────────────────┐   │
│  │ - RRDBNet (23-block)             │   │
│  │ - Real-ESRGAN Model (x2)         │   │
│  │ - Image Processing Pipeline      │   │
│  └──────────────────────────────────┘   │
└──────────┬──────────────────────────────┘
           │
┌──────────▼──────────────────────────────┐
│  Modal Volume Storage                   │
│  (RealESRGAN_x2plus.pth)                │
└─────────────────────────────────────────┘
```

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Modal Account**: Create one at [https://modal.com](https://modal.com)
- **Modal Token**: Set up authentication
- **Git**: For version control
- **RealESRGAN Weights**: Pre-trained model file (~350MB)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/chaitanykakde/Pixora-Ai-.git
cd Pixora-Ai-
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Modal CLI

```bash
pip install modal
```

### 4. Authenticate with Modal

```bash
modal token new
```

This will open your browser to create and copy your authentication token. Follow the prompts to complete authentication.

### 5. Obtain Model Weights

Download the Real-ESRGAN x2plus model weights from:
- [Official Model Repository](https://github.com/xinntao/Real-ESRGAN/releases)
- Direct download: `RealESRGAN_x2plus.pth` (~350MB)

Place the weights file at:
```
../models/RealESRGAN_x2plus.pth
```

## ⚙️ Configuration

### Modal Volume Setup

The application uses a Modal Volume named `pixora-models` to store model weights. This is created automatically on first deployment.

### Environment Variables

Optional configuration via environment:
- `MODAL_WORKSPACE`: Specify Modal workspace (defaults to current)
- `SCALEDOWN_WINDOW`: GPU scaledown timeout (default: 300 seconds)

## 📖 Usage

### Option 1: Deploy to Modal (Production)

```bash
# Upload model weights to Modal volume
python upload_weights_to_modal.py

# Deploy the app
modal deploy modal_app.py
```

This will:
1. Validate model weights
2. Upload to Modal Volume
3. Deploy the application
4. Provide a public HTTPS URL

### Option 2: Local Development (with Modal)

```bash
modal serve modal_app.py
```

This creates a local development server with hot-reload capabilities.

## 📡 API Documentation

### Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "ok",
  "service": "pixora-modal"
}
```

### Image Enhancement

**Endpoint**: `POST /enhance`

**Parameters**:
- `strength` (query): Enhancement blend factor [0.0-1.0], default: 0.7
- `output_format` (query): Output image format ["jpeg", "png"], default: "jpeg"
- Binary image data in request body

**Request Example**:
```bash
curl -X POST "https://your-app.modal.run/enhance?strength=0.8&output_format=jpeg" \
  --data-binary @input.jpg \
  --output output.jpg
```

**Python Example**:
```python
import requests

with open("image.jpg", "rb") as f:
    response = requests.post(
        "https://your-app.modal.run/enhance",
        params={
            "strength": 0.8,
            "output_format": "jpeg"
        },
        data=f.read()
    )
    
if response.status_code == 200:
    with open("enhanced.jpg", "wb") as out:
        out.write(response.content)
```

**Response**:
- **Success (200)**: Binary image data with Content-Type header (image/jpeg or image/png)
- **Error (400)**: 
```json
{
  "error": "Invalid strength value."
}
```
- **Error (500)**:
```json
{
  "error": "Inference error: [details]"
}
```

### Web Frontend

**Endpoint**: `GET /` (and any path)

Serves the interactive web frontend. Upload images through the browser UI for visual feedback.

## 🌐 Deployment

### Prerequisites for Deployment

1. Modal account with sufficient GPU quota
2. Model weights uploaded to Modal Volume
3. Git repository with up-to-date code

### Deployment Steps

```bash
# 1. Ensure you're in the project directory
cd Pixora-Ai-

# 2. Upload model weights
python upload_weights_to_modal.py

# 3. Deploy the application
modal deploy modal_app.py

# 4. Monitor deployment
modal logs pixora-ai-enhance
```

### Scaling Configuration

The app is configured with:
- **GPU**: A10G (24GB VRAM)
- **Scaledown Window**: 300 seconds (auto-shutdown after idle)
- **Concurrency**: Auto-scaled based on queue

### Cost Optimization

- GPU only runs during inference
- Automatic scaledown after 5 minutes of inactivity
- Efficient tile-based processing to fit large images

## 📁 Project Structure

```
Pixora-Ai-/
├── modal_app.py                      # Main Modal application
├── upload_weights_to_modal.py        # Utility to upload model weights
├── README.md                         # Project documentation
├── .git/                             # Git repository
└── __pycache__/                      # Python cache
```

### Key Files

**`modal_app.py`**
- Main application entry point
- Defines Modal app, GPU service, and web server
- Handles image enhancement requests
- Serves web frontend

**`upload_weights_to_modal.py`**
- Utility script to upload model weights
- Manages Modal volume operations
- Validates weight file existence

## 🔧 Troubleshooting

### Modal Authentication Issues

```bash
# Reset authentication
modal token clear
modal token new
```

### Model Weights Not Found

```bash
# Check weights location
ls ../models/RealESRGAN_x2plus.pth

# Re-upload if missing
python upload_weights_to_modal.py
```

### GPU Memory Issues

The app uses efficient tiling with:
- `tile=0` (auto-tile)
- `tile_pad=10` (overlap padding)
- `pre_pad=0`
- `half=True` (FP16 precision for memory efficiency)

### Slow Inference

1. Check GPU availability: `modal gpu ls`
2. Verify model is loaded: Check Modal logs
3. Monitor queue: `modal logs pixora-ai-enhance`

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) for the super-resolution model
- [BasicSR](https://github.com/XPixelGroup/BasicSR) framework
- [Modal](https://modal.com) for serverless GPU infrastructure

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check Modal documentation: https://modal.com/docs
- Real-ESRGAN docs: https://github.com/xinntao/Real-ESRGAN

---

**Last Updated**: May 2026  
**Maintainer**: Vishal Bhutekar  
**Status**: Active Development
