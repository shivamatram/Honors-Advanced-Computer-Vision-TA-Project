/**
 * VideoFeed — Core component: webcam capture + canvas overlay for bounding boxes
 * 
 * Architecture:
 *   1. getUserMedia → <video> (hidden processing source)
 *   2. setInterval captures frames → canvas.toBlob() → sendFrame(blob)
 *   3. Receives emotion data JSON → draws bounding boxes + labels on overlay canvas
 */
import { useRef, useEffect, useCallback, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { VideoOff, Scan } from 'lucide-react';

const FRAME_INTERVAL = 150; // ms between frames (~7 fps sending rate)
const EMOTION_COLORS = {
  happy: '#10b981',
  sad: '#3b82f6',
  angry: '#ef4444',
  surprise: '#f97316',
  fear: '#a855f7',
  disgust: '#eab308',
  neutral: '#06b6d4',
};

const EMOTION_EMOJIS = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  surprise: '😲',
  fear: '😨',
  disgust: '🤢',
  neutral: '😐',
};

export default function VideoFeed({ isStreaming, sendFrame, emotionData, onSnapshotRef }) {
  const videoRef = useRef(null);
  const canvasOverlayRef = useRef(null);
  const captureCanvasRef = useRef(null);
  const streamRef = useRef(null);
  const intervalRef = useRef(null);
  const [videoReady, setVideoReady] = useState(false);
  const [videoDimensions, setVideoDimensions] = useState({ width: 640, height: 480 });

  // Start/stop webcam
  useEffect(() => {
    if (isStreaming) {
      startCamera();
    } else {
      stopCamera();
    }

    return () => stopCamera();
  }, [isStreaming]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user',
        },
        audio: false,
      });

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current.play();
          const { videoWidth, videoHeight } = videoRef.current;
          setVideoDimensions({ width: videoWidth, height: videoHeight });
          setVideoReady(true);
        };
      }
    } catch (err) {
      console.error('Failed to access webcam:', err);
    }
  };

  const stopCamera = () => {
    setVideoReady(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    // Clear overlay
    if (canvasOverlayRef.current) {
      const ctx = canvasOverlayRef.current.getContext('2d');
      ctx.clearRect(0, 0, canvasOverlayRef.current.width, canvasOverlayRef.current.height);
    }
  };

  // Send frames to backend at interval
  useEffect(() => {
    if (!videoReady || !isStreaming) return;

    const captureCanvas = captureCanvasRef.current;
    const video = videoRef.current;
    if (!captureCanvas || !video) return;

    captureCanvas.width = videoDimensions.width;
    captureCanvas.height = videoDimensions.height;
    const ctx = captureCanvas.getContext('2d');

    intervalRef.current = setInterval(() => {
      if (video.readyState >= 2) {
        ctx.drawImage(video, 0, 0, captureCanvas.width, captureCanvas.height);
        captureCanvas.toBlob(
          (blob) => {
            if (blob) sendFrame(blob);
          },
          'image/jpeg',
          0.7
        );
      }
    }, FRAME_INTERVAL);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [videoReady, isStreaming, sendFrame, videoDimensions]);

  // Draw bounding boxes + emotion labels
  useEffect(() => {
    if (!emotionData || !canvasOverlayRef.current) return;

    const canvas = canvasOverlayRef.current;
    const ctx = canvas.getContext('2d');
    
    // Scale canvas to match displayed size
    const displayEl = canvas.parentElement;
    const scaleX = canvas.width / videoDimensions.width;
    const scaleY = canvas.height / videoDimensions.height;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!emotionData.faces || emotionData.faces.length === 0) return;

    emotionData.faces.forEach((face, index) => {
      const { bbox, dominant, emotions } = face;
      const { x, y, w, h } = bbox;

      // Scale coordinates
      const sx = x * scaleX;
      const sy = y * scaleY;
      const sw = w * scaleX;
      const sh = h * scaleY;

      const color = EMOTION_COLORS[dominant] || '#00f0ff';
      const emoji = EMOTION_EMOJIS[dominant] || '🤔';
      const confidence = emotions?.[dominant] ? Math.round(emotions[dominant]) : 0;

      // Draw bounding box with rounded corners
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      ctx.shadowColor = color;
      ctx.shadowBlur = 12;

      const radius = 12;
      drawRoundedRect(ctx, sx, sy, sw, sh, radius);
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Corner accents (sci-fi style)
      const cornerLen = 18;
      ctx.lineWidth = 3;
      ctx.strokeStyle = color;
      ctx.shadowColor = color;
      ctx.shadowBlur = 8;

      // Top-left
      drawCorner(ctx, sx, sy, cornerLen, 'tl');
      // Top-right
      drawCorner(ctx, sx + sw, sy, cornerLen, 'tr');
      // Bottom-left
      drawCorner(ctx, sx, sy + sh, cornerLen, 'bl');
      // Bottom-right
      drawCorner(ctx, sx + sw, sy + sh, cornerLen, 'br');
      
      ctx.shadowBlur = 0;

      // Emotion label background
      const label = `${emoji} ${dominant.toUpperCase()} ${confidence}%`;
      ctx.font = 'bold 13px "Inter", system-ui, sans-serif';
      const labelWidth = ctx.measureText(label).width + 16;
      const labelHeight = 26;
      const labelX = sx;
      const labelY = sy - labelHeight - 6;

      // Label background with gradient
      ctx.fillStyle = `${color}22`;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      drawRoundedRect(ctx, labelX, labelY, labelWidth, labelHeight, 8);
      ctx.fill();
      ctx.stroke();

      // Label text
      ctx.fillStyle = color;
      ctx.shadowColor = color;
      ctx.shadowBlur = 6;
      ctx.fillText(label, labelX + 8, labelY + 17);
      ctx.shadowBlur = 0;
    });
  }, [emotionData, videoDimensions]);

  // Expose snapshot function
  useEffect(() => {
    if (onSnapshotRef) {
      onSnapshotRef.current = takeSnapshot;
    }
  });

  const takeSnapshot = useCallback(() => {
    if (!videoRef.current || !canvasOverlayRef.current) return;

    const snapshotCanvas = document.createElement('canvas');
    snapshotCanvas.width = videoDimensions.width;
    snapshotCanvas.height = videoDimensions.height;
    const ctx = snapshotCanvas.getContext('2d');

    // Draw video frame
    ctx.drawImage(videoRef.current, 0, 0, snapshotCanvas.width, snapshotCanvas.height);
    // Draw overlay (bounding boxes)
    ctx.drawImage(canvasOverlayRef.current, 0, 0, snapshotCanvas.width, snapshotCanvas.height);

    // Download
    const link = document.createElement('a');
    link.download = `emotisense-snapshot-${Date.now()}.png`;
    link.href = snapshotCanvas.toDataURL('image/png');
    link.click();
  }, [videoDimensions]);

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      {/* Video container */}
      <div className="video-container relative w-full" style={{ aspectRatio: '4/3' }}>
        {/* Actual video */}
        <video
          ref={videoRef}
          className="absolute inset-0 w-full h-full object-cover rounded-2xl"
          playsInline
          muted
          style={{ transform: 'scaleX(-1)' }}
        />

        {/* Overlay canvas for bounding boxes */}
        <canvas
          ref={canvasOverlayRef}
          width={videoDimensions.width}
          height={videoDimensions.height}
          className="absolute inset-0 w-full h-full rounded-2xl pointer-events-none"
          style={{ transform: 'scaleX(-1)' }}
        />

        {/* Hidden capture canvas */}
        <canvas ref={captureCanvasRef} className="hidden" />

        {/* Scanning overlay effect */}
        <AnimatePresence>
          {isStreaming && videoReady && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 rounded-2xl scan-line pointer-events-none"
            />
          )}
        </AnimatePresence>

        {/* No camera placeholder */}
        <AnimatePresence>
          {!isStreaming && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 flex flex-col items-center justify-center bg-surface-900/90 rounded-2xl"
            >
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <VideoOff className="w-16 h-16 text-slate-600 mb-4" />
              </motion.div>
              <p className="text-slate-500 font-medium">Camera is off</p>
              <p className="text-slate-600 text-sm mt-1">Click "Start Camera" to begin</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Face count badge */}
        <AnimatePresence>
          {isStreaming && emotionData?.face_count > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5 }}
              className="absolute top-3 left-3 flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-800/80 backdrop-blur-sm border border-accent-cyan/20"
            >
              <Scan className="w-3.5 h-3.5 text-accent-cyan" />
              <span className="text-xs font-mono text-accent-cyan">
                {emotionData.face_count} {emotionData.face_count === 1 ? 'FACE' : 'FACES'}
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ===== Canvas Drawing Helpers =====

function drawRoundedRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function drawCorner(ctx, x, y, len, position) {
  ctx.beginPath();
  switch (position) {
    case 'tl':
      ctx.moveTo(x, y + len);
      ctx.lineTo(x, y);
      ctx.lineTo(x + len, y);
      break;
    case 'tr':
      ctx.moveTo(x - len, y);
      ctx.lineTo(x, y);
      ctx.lineTo(x, y + len);
      break;
    case 'bl':
      ctx.moveTo(x, y - len);
      ctx.lineTo(x, y);
      ctx.lineTo(x + len, y);
      break;
    case 'br':
      ctx.moveTo(x - len, y);
      ctx.lineTo(x, y);
      ctx.lineTo(x, y - len);
      break;
  }
  ctx.stroke();
}
