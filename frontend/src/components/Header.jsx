/**
 * Header — Top navigation bar with app title, status, and FPS counter
 */
import { motion } from 'framer-motion';
import { Brain, Activity, Wifi, WifiOff } from 'lucide-react';

export default function Header({ isConnected, connectionStatus, processingTime, isStreaming }) {
  const fps = processingTime > 0 ? Math.min(Math.round(1000 / processingTime), 30) : 0;

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="flex items-center justify-between px-6 py-4 glass-card rounded-none border-x-0 border-t-0"
    >
      {/* Logo & Title */}
      <div className="flex items-center gap-3">
        <motion.div
          animate={{ rotate: isStreaming ? 360 : 0 }}
          transition={{ duration: 3, repeat: isStreaming ? Infinity : 0, ease: 'linear' }}
          className="relative"
        >
          <Brain className="w-8 h-8 text-accent-cyan" />
          <div className="absolute inset-0 w-8 h-8 bg-accent-cyan/20 blur-lg rounded-full" />
        </motion.div>
        <div>
          <h1 className="font-display text-xl font-bold tracking-wider text-glow-cyan text-accent-cyan">
            EMOTISENSE AI
          </h1>
          <p className="text-xs text-slate-500 font-mono tracking-widest">
            FACIAL EMOTION RECOGNITION
          </p>
        </div>
      </div>

      {/* Status Indicators */}
      <div className="flex items-center gap-6">
        {/* FPS Counter */}
        {isStreaming && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-700/50 border border-white/5"
          >
            <Activity className="w-3.5 h-3.5 text-neon-green" />
            <span className="font-mono text-xs text-neon-green">
              {fps} FPS
            </span>
            <span className="text-slate-600 mx-1">|</span>
            <span className="font-mono text-xs text-slate-400">
              {processingTime.toFixed(0)}ms
            </span>
          </motion.div>
        )}

        {/* Connection Status */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-surface-700/50 border border-white/5">
          {isConnected ? (
            <Wifi className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <WifiOff className="w-3.5 h-3.5 text-red-400" />
          )}
          <span className={`text-xs font-medium ${
            connectionStatus === 'connected' ? 'text-emerald-400' :
            connectionStatus === 'reconnecting' ? 'text-amber-400' :
            'text-red-400'
          }`}>
            {connectionStatus === 'connected' ? 'CONNECTED' :
             connectionStatus === 'reconnecting' ? 'RECONNECTING...' :
             'OFFLINE'}
          </span>
          <div className={`${
            connectionStatus === 'connected' ? 'status-dot-active' :
            'status-dot-inactive'
          }`} />
        </div>
      </div>
    </motion.header>
  );
}
