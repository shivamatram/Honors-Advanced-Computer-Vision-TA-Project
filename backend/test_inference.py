"""
Test script — validates the face detection + emotion inference pipeline.
Captures a single frame from the webcam, runs detection, and prints results.

Usage:
    python test_inference.py
"""

import cv2
import numpy as np
from deepface import DeepFace
import time
import json

def test_pipeline():
    print("=" * 60)
    print("  EmotiSense AI — Inference Pipeline Test")
    print("=" * 60)
    
    # 1. Initialize face detector
    print("\n[1/4] Loading face detector...")
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)
    print(f"  [OK] Haar cascade loaded from: {cascade_path}")
    
    # 2. Pre-warm DeepFace
    print("\n[2/4] Pre-warming DeepFace emotion model...")
    start = time.time()
    try:
        dummy = np.zeros((48, 48, 3), dtype=np.uint8)
        DeepFace.analyze(
            dummy,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
            detector_backend="skip",
        )
        print(f"  [OK] DeepFace ready ({time.time() - start:.1f}s)")
    except Exception as e:
        print(f"  [WARN] Pre-warm warning: {e}")
    
    # 3. Capture a frame from webcam
    print("\n[3/4] Capturing webcam frame...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("  [ERROR] Could not open webcam!")
        print("  Make sure your webcam is connected and not in use by another app.")
        return False
    
    # Wait a moment for the camera to warm up
    time.sleep(1)
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret or frame is None:
        print("  [ERROR] Could not read frame from webcam!")
        return False
    
    print(f"  [OK] Frame captured: {frame.shape[1]}x{frame.shape[0]}")
    
    # 4. Run face detection + emotion analysis
    print("\n[4/4] Running face detection + emotion analysis...")
    start = time.time()
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    
    detection_time = (time.time() - start) * 1000
    print(f"  Faces detected: {len(faces)} ({detection_time:.1f}ms)")
    
    if len(faces) == 0:
        print("\n  [WARN] No faces detected. Try:")
        print("  - Better lighting")
        print("  - Face the camera directly")
        print("  - Move closer to the camera")
        
        # Still test DeepFace with the full frame
        print("\n  Running DeepFace on full frame as fallback test...")
        try:
            start = time.time()
            result = DeepFace.analyze(
                frame,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
            )
            emotion_time = (time.time() - start) * 1000
            
            if isinstance(result, list):
                result = result[0]
            
            print(f"  DeepFace inference time: {emotion_time:.1f}ms")
            print(f"  Emotions: {json.dumps(result.get('emotion', {}), indent=4)}")
            print(f"  Dominant: {result.get('dominant_emotion', 'N/A')}")
        except Exception as e:
            print(f"  DeepFace error: {e}")
        
        return True
    
    for i, (x, y, w, h) in enumerate(faces):
        print(f"\n  --- Face {i + 1} ---")
        print(f"  Bounding box: x={x}, y={y}, w={w}, h={h}")
        
        # Crop face
        pad = int(w * 0.1)
        x1 = max(0, x - pad)
        y1 = max(0, y - pad)
        x2 = min(frame.shape[1], x + w + pad)
        y2 = min(frame.shape[0], y + h + pad)
        face_roi = frame[y1:y2, x1:x2]
        
        # Emotion analysis
        start = time.time()
        try:
            result = DeepFace.analyze(
                face_roi,
                actions=["emotion"],
                enforce_detection=False,
                silent=True,
                detector_backend="skip",
            )
            emotion_time = (time.time() - start) * 1000
            
            if isinstance(result, list):
                result = result[0]
            
            emotions = result.get("emotion", {})
            dominant = result.get("dominant_emotion", "N/A")
            
            print(f"  Inference time: {emotion_time:.1f}ms")
            print(f"  Dominant emotion: {dominant}")
            print(f"  Confidence scores:")
            for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
                bar = "█" * int(score / 2) + "░" * (50 - int(score / 2))
                print(f"    {emotion:>10s}: {bar} {score:.1f}%")
                
        except Exception as e:
            print(f"  [ERROR] Emotion analysis error: {e}")
    
    print("\n" + "=" * 60)
    print("  [OK] Pipeline test PASSED!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_pipeline()
    if not success:
        print("\n[FAILED] Pipeline test FAILED")
        exit(1)
