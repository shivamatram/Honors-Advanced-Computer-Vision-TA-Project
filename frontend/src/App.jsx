/**
 * App.jsx — Main layout for EmotiSense AI
 * 
 * Layout:
 *   ┌─────────────────────────────────────────────────┐
 *   │  Header (logo, status, FPS)                     │
 *   ├────────────────────────────┬────────────────────┤
 *   │                            │  Emotion Dashboard │
 *   │     Video Feed             │  - Dominant        │
 *   │     (webcam + overlay)     │  - Radar Chart     │
 *   │                            │  - Progress Bars   │
 *   ├────────────────────────────┴────────────────────┤
 *   │  Controls (camera toggle, snapshot)             │
 *   └─────────────────────────────────────────────────┘
 */
import { useState, useRef, useCallback, useEffect } from 'react';
import { motion } from 'framer-motion';
import Header from './components/Header';
import VideoFeed from './components/VideoFeed';
import EmotionDashboard from './components/EmotionDashboard';
import Controls from './components/Controls';
import { useWebSocket } from './hooks/useWebSocket';

function App() {
  const [isStreaming, setIsStreaming] = useState(false);
  const snapshotRef = useRef(null);
  
  const {
    isConnected,
    connectionStatus,
    emotionData,
    processingTime,
    connect,
    disconnect,
    sendFrame,
  } = useWebSocket();

  // Connect to backend when streaming starts
  useEffect(() => {
    if (isStreaming) {
      connect();
    }
    return () => {
      // Keep connection alive unless explicitly stopped
    };
  }, [isStreaming, connect]);

  const handleToggleCamera = useCallback(() => {
    if (isStreaming) {
      setIsStreaming(false);
      disconnect();
    } else {
      setIsStreaming(true);
    }
  }, [isStreaming, disconnect]);

  const handleSnapshot = useCallback(() => {
    if (snapshotRef.current) {
      snapshotRef.current();
    }
  }, []);

  return (
    <div className="min-h-screen bg-surface-900 bg-cyber-grid flex flex-col">
      {/* Header */}
      <Header
        isConnected={isConnected}
        connectionStatus={connectionStatus}
        processingTime={processingTime}
        isStreaming={isStreaming}
      />

      {/* Main Content */}
      <main className="flex-1 flex flex-col lg:flex-row gap-4 p-4 lg:p-6 overflow-hidden">
        {/* Video Feed — Left Panel */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6 }}
          className="flex-1 lg:flex-[2] min-h-0"
        >
          <div className="glass-card p-3 h-full flex flex-col">
            <div className="flex items-center gap-2 px-2 py-2 mb-2">
              <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-red-500 animate-pulse' : 'bg-slate-600'}`} />
              <span className="text-xs font-mono text-slate-500 tracking-wider uppercase">
                {isStreaming ? 'LIVE FEED' : 'STANDBY'}
              </span>
            </div>
            <div className="flex-1 flex items-center justify-center">
              <VideoFeed
                isStreaming={isStreaming}
                sendFrame={sendFrame}
                emotionData={emotionData}
                onSnapshotRef={snapshotRef}
              />
            </div>
          </div>
        </motion.div>

        {/* Dashboard — Right Panel */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="lg:flex-1 lg:max-w-sm xl:max-w-md min-h-0"
        >
          <EmotionDashboard
            emotionData={emotionData}
            isStreaming={isStreaming}
          />
        </motion.div>
      </main>

      {/* Controls — Bottom Bar */}
      <div className="p-4 lg:p-6 pt-0">
        <div className="glass-card p-4">
          <Controls
            isStreaming={isStreaming}
            onToggleCamera={handleToggleCamera}
            onSnapshot={handleSnapshot}
            isConnected={isConnected}
          />
        </div>
      </div>
    </div>
  );
}

export default App;
