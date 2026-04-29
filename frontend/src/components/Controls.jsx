/**
 * Controls — Camera toggle and snapshot buttons with connection status
 */
import { motion } from 'framer-motion';
import { Camera, CameraOff, Download, Zap, ZapOff } from 'lucide-react';

export default function Controls({ isStreaming, onToggleCamera, onSnapshot, isConnected }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="flex items-center justify-center gap-4 flex-wrap"
    >
      {/* Toggle Camera Button */}
      <motion.button
        id="toggle-camera-btn"
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={onToggleCamera}
        className={`group flex items-center gap-3 px-8 py-3.5 rounded-xl font-semibold text-sm tracking-wider uppercase transition-all duration-300 ${
          isStreaming
            ? 'bg-gradient-to-r from-red-500/10 to-pink-500/10 border border-red-500/30 text-red-400 hover:border-red-500/60 hover:shadow-[0_0_20px_rgba(239,68,68,0.15)]'
            : 'bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border border-accent-cyan/30 text-accent-cyan hover:border-accent-cyan/60 hover:shadow-glow-cyan'
        }`}
      >
        {isStreaming ? (
          <>
            <CameraOff className="w-5 h-5 transition-transform group-hover:scale-110" />
            <span>Stop Camera</span>
          </>
        ) : (
          <>
            <Camera className="w-5 h-5 transition-transform group-hover:scale-110" />
            <span>Start Camera</span>
          </>
        )}
      </motion.button>

      {/* Snapshot Button */}
      <motion.button
        id="snapshot-btn"
        whileHover={{ scale: 1.03 }}
        whileTap={{ scale: 0.97 }}
        onClick={onSnapshot}
        disabled={!isStreaming}
        className={`group flex items-center gap-3 px-8 py-3.5 rounded-xl font-semibold text-sm tracking-wider uppercase transition-all duration-300 ${
          isStreaming
            ? 'bg-gradient-to-r from-purple-500/10 to-indigo-500/10 border border-neon-purple/30 text-neon-purple hover:border-neon-purple/60 hover:shadow-glow-purple'
            : 'bg-surface-800/30 border border-white/5 text-slate-600 cursor-not-allowed'
        }`}
      >
        <Download className="w-5 h-5 transition-transform group-hover:scale-110" />
        <span>Snapshot</span>
      </motion.button>

      {/* Backend connection indicator */}
      <motion.div
        whileHover={{ scale: 1.03 }}
        className={`flex items-center gap-2 px-5 py-3.5 rounded-xl text-xs font-mono border transition-all duration-300 ${
          isConnected
            ? 'border-emerald-500/20 text-emerald-400 bg-emerald-500/5'
            : 'border-red-500/20 text-red-400 bg-red-500/5'
        }`}
      >
        {isConnected ? (
          <Zap className="w-4 h-4" />
        ) : (
          <ZapOff className="w-4 h-4" />
        )}
        <span>{isConnected ? 'AI ACTIVE' : 'AI OFFLINE'}</span>
      </motion.div>
    </motion.div>
  );
}
