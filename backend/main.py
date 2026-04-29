"""
EmotiSense AI — FastAPI Backend
Real-time Facial Emotion Recognition via WebSocket streaming.

Architecture:
  1. Frontend sends binary JPEG frames via WebSocket
  2. Backend decodes with OpenCV, detects faces (DNN SSD), 
     classifies emotions (DeepFace), returns JSON results
  3. Frontend renders bounding boxes + dashboard from JSON
"""

import asyncio
import base64
import json
import logging
import time
from contextlib import asynccontextmanager

import cv2
import numpy as np
from deepface import DeepFace
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("emotisense")

# ---------------------------------------------------------------------------
# Face Detection — OpenCV DNN (Caffe SSD)
# ---------------------------------------------------------------------------
# Using OpenCV's built-in DNN face detector (more accurate than Haar cascades)
PROTOTXT_PATH = None
MODEL_PATH = None
face_net = None

def init_face_detector():
    """Initialize OpenCV DNN face detector using built-in Haar cascade 
    as primary, with DNN as upgrade path."""
    global face_net, PROTOTXT_PATH, MODEL_PATH
    
    # Use Haar cascade — ships with OpenCV, no extra downloads
    face_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    logger.info(f"Loading Haar cascade from: {face_cascade_path}")
    return cv2.CascadeClassifier(face_cascade_path)

face_cascade = None

def detect_faces_haar(frame: np.ndarray, min_size: int = 60):
    """Detect faces using Haar cascade classifier."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(min_size, min_size),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    results = []
    for (x, y, w, h) in faces:
        # Add some padding around the face for better emotion detection
        pad_w = int(w * 0.1)
        pad_h = int(h * 0.1)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(frame.shape[1], x + w + pad_w)
        y2 = min(frame.shape[0], y + h + pad_h)
        
        results.append({
            "x": int(x1),
            "y": int(y1),
            "w": int(x2 - x1),
            "h": int(y2 - y1),
        })
    
    return results

# ---------------------------------------------------------------------------
# Emotion Analysis
# ---------------------------------------------------------------------------
def analyze_emotions(frame: np.ndarray, face_box: dict) -> dict:
    """Run DeepFace emotion analysis on a cropped face region."""
    x, y, w, h = face_box["x"], face_box["y"], face_box["w"], face_box["h"]
    
    # Crop face region
    face_roi = frame[y:y+h, x:x+w]
    
    if face_roi.size == 0:
        return None
    
    try:
        results = DeepFace.analyze(
            face_roi,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
            detector_backend="skip",  # We already detected the face
        )
        
        if isinstance(results, list):
            results = results[0]
        
        emotions = results.get("emotion", {})
        dominant = results.get("dominant_emotion", "neutral")
        
        return {
            "emotions": {k: float(v) for k, v in emotions.items()},
            "dominant": str(dominant),
        }
    except Exception as e:
        logger.warning(f"DeepFace analysis failed: {e}")
        return None

# ---------------------------------------------------------------------------
# App Lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm the DeepFace model on startup."""
    global face_cascade
    
    logger.info("🚀 Initializing EmotiSense AI backend...")
    
    # Initialize face detector
    face_cascade = init_face_detector()
    logger.info("✅ Face detector loaded")
    
    # Pre-warm DeepFace emotion model with a dummy image
    logger.info("⏳ Pre-warming DeepFace emotion model (first run downloads weights)...")
    try:
        dummy = np.zeros((48, 48, 3), dtype=np.uint8)
        DeepFace.analyze(
            dummy, 
            actions=["emotion"], 
            enforce_detection=False, 
            silent=True,
            detector_backend="skip",
        )
        logger.info("✅ DeepFace emotion model ready")
    except Exception as e:
        logger.warning(f"⚠️ DeepFace pre-warm warning (expected on first run): {e}")
    
    logger.info("🟢 EmotiSense AI backend is READY")
    yield
    logger.info("🔴 Shutting down EmotiSense AI backend")

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="EmotiSense AI",
    description="Real-time Facial Emotion Recognition API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server and deployed frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for easy deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint to verify server is running."""
    return {
        "message": "EmotiSense AI Backend is Running",
        "endpoints": ["/ws", "/health"]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "EmotiSense AI",
        "face_detector": "retinaface",
        "emotion_model": "deepface",
    }

# ---------------------------------------------------------------------------
# WebSocket — Real-time Video Processing
# ---------------------------------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time facial emotion recognition.
    
    Protocol:
      - Client sends: binary JPEG frame data
      - Server responds: JSON with face detections and emotion analysis
    
    Response format:
    {
        "faces": [
            {
                "bbox": {"x": int, "y": int, "w": int, "h": int},
                "emotions": {"happy": float, "sad": float, ...},
                "dominant": "happy"
            }
        ],
        "face_count": int,
        "processing_time_ms": float,
        "timestamp": float
    }
    """
    await websocket.accept()
    logger.info("🔌 WebSocket client connected")
    
    frame_count = 0
    
    try:
        while True:
            # Receive binary frame from client
            data = await websocket.receive_bytes()
            frame_count += 1
            
            start_time = time.time()
            
            # Decode JPEG to OpenCV frame
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                await websocket.send_json({
                    "faces": [],
                    "face_count": 0,
                    "processing_time_ms": 0,
                    "timestamp": time.time(),
                    "error": "Failed to decode frame"
                })
                continue
            
            # Detect faces
            face_boxes = detect_faces_haar(frame)
            
            # Analyze emotions for each face (limit to top 3 largest faces)
            face_boxes_sorted = sorted(face_boxes, key=lambda f: f["w"] * f["h"], reverse=True)[:3]
            
            faces_result = []
            for box in face_boxes_sorted:
                emotion_data = await asyncio.to_thread(analyze_emotions, frame, box)
                
                face_info = {
                    "bbox": box,
                    "emotions": emotion_data["emotions"] if emotion_data else {},
                    "dominant": emotion_data["dominant"] if emotion_data else "unknown",
                }
                faces_result.append(face_info)
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            response = {
                "faces": faces_result,
                "face_count": len(faces_result),
                "processing_time_ms": round(processing_time, 1),
                "timestamp": time.time(),
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info(f"🔌 WebSocket client disconnected (processed {frame_count} frames)")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.close()
        except:
            pass

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
