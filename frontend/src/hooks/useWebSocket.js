/**
 * useWebSocket — Custom React hook for WebSocket communication
 * Handles connection, auto-reconnection, frame sending, and emotion data parsing.
 */
import { useState, useEffect, useRef, useCallback } from 'react';

// Use environment variable for production, fallback to localhost for development
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
const RECONNECT_DELAY_BASE = 1000;
const MAX_RECONNECT_DELAY = 10000;

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected'); // 'connected' | 'disconnected' | 'reconnecting'
  const [emotionData, setEmotionData] = useState(null);
  const [processingTime, setProcessingTime] = useState(0);
  
  const wsRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const isIntentionalClose = useRef(false);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    
    try {
      const ws = new WebSocket(WS_URL);
      ws.binaryType = 'arraybuffer';
      
      ws.onopen = () => {
        console.log('[WS] Connected to EmotiSense backend');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttemptRef.current = 0;
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setEmotionData(data);
          setProcessingTime(data.processing_time_ms || 0);
        } catch (e) {
          console.warn('[WS] Failed to parse message:', e);
        }
      };
      
      ws.onclose = (event) => {
        console.log('[WS] Disconnected', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;
        
        if (!isIntentionalClose.current) {
          setConnectionStatus('reconnecting');
          const delay = Math.min(
            RECONNECT_DELAY_BASE * Math.pow(2, reconnectAttemptRef.current),
            MAX_RECONNECT_DELAY
          );
          reconnectAttemptRef.current++;
          console.log(`[WS] Reconnecting in ${delay}ms (attempt ${reconnectAttemptRef.current})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        } else {
          setConnectionStatus('disconnected');
        }
      };
      
      ws.onerror = (error) => {
        console.error('[WS] Error:', error);
      };
      
      wsRef.current = ws;
    } catch (e) {
      console.error('[WS] Connection failed:', e);
      setConnectionStatus('disconnected');
    }
  }, []);

  const disconnect = useCallback(() => {
    isIntentionalClose.current = true;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
    setConnectionStatus('disconnected');
  }, []);

  const sendFrame = useCallback((blob) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(blob);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      isIntentionalClose.current = true;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  return {
    isConnected,
    connectionStatus,
    emotionData,
    processingTime,
    connect,
    disconnect,
    sendFrame,
  };
}
