/**
 * EmotionDashboard — Sidebar panel with dominant emotion, radar chart, and progress bars
 */
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Users } from 'lucide-react';
import EmotionBars from './EmotionBars';

const EMOTION_EMOJIS = {
  happy: '😊',
  sad: '😢',
  angry: '😠',
  surprise: '😲',
  fear: '😨',
  disgust: '🤢',
  neutral: '😐',
};

const EMOTION_COLORS = {
  happy: '#10b981',
  sad: '#3b82f6',
  angry: '#ef4444',
  surprise: '#f97316',
  fear: '#a855f7',
  disgust: '#eab308',
  neutral: '#06b6d4',
};

export default function EmotionDashboard({ emotionData, isStreaming }) {
  const primaryFace = emotionData?.faces?.[0];
  const emotions = primaryFace?.emotions || {};
  const dominant = primaryFace?.dominant || null;
  const faceCount = emotionData?.face_count || 0;
  const hasData = dominant && Object.keys(emotions).length > 0;

  const confidence = hasData ? Math.round(emotions[dominant] || 0) : 0;
  const dominantColor = EMOTION_COLORS[dominant] || '#00f0ff';
  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (confidence / 100) * circumference;

  return (
    <motion.aside
      initial={{ opacity: 0, x: 30 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay: 0.1 }}
      className="h-full flex flex-col gap-6 overflow-y-auto pr-1"
    >
      {/* 1. Main Status Card (Top, Greatly Enhanced) */}
      <div className="glass-card p-6 flex flex-col items-center justify-between min-h-[400px] relative overflow-hidden">
        <div className="w-full flex items-center gap-2 mb-2 absolute top-5 left-5">
          <Sparkles className="w-4 h-4 text-accent-cyan" />
          <h2 className="text-xs font-mono text-slate-500 tracking-widest uppercase">
            Primary Status
          </h2>
        </div>

        <div className="flex-1 w-full flex flex-col items-center justify-center mt-6">
          <AnimatePresence mode="wait">
            {hasData ? (
              <motion.div
                key={dominant}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.3 }}
                className="flex flex-col items-center"
              >
                {/* Radial Gauge */}
                <div className="relative flex items-center justify-center mb-6 w-40 h-40">
                  <svg className="absolute inset-0 w-full h-full transform -rotate-90">
                    <circle
                      cx="80"
                      cy="80"
                      r={radius}
                      stroke="rgba(255,255,255,0.05)"
                      strokeWidth="6"
                      fill="transparent"
                    />
                    <motion.circle
                      cx="80"
                      cy="80"
                      r={radius}
                      stroke={dominantColor}
                      strokeWidth="6"
                      fill="transparent"
                      strokeDasharray={circumference}
                      initial={{ strokeDashoffset: circumference }}
                      animate={{ strokeDashoffset }}
                      transition={{ duration: 0.5, ease: 'easeOut' }}
                      style={{ filter: `drop-shadow(0 0 12px ${dominantColor}80)` }}
                      strokeLinecap="round"
                    />
                  </svg>
                  <span className="text-7xl relative z-10 block leading-none pt-2">{EMOTION_EMOJIS[dominant] || '🤔'}</span>
                </div>
                
                <h3 
                  className="text-3xl font-black tracking-widest uppercase mb-1 text-center"
                  style={{ color: dominantColor, textShadow: `0 0 15px ${dominantColor}50` }}
                >
                  {dominant}
                </h3>
                <p className="text-lg text-slate-300 font-mono font-medium">
                  Confidence: <span className="text-white font-bold">{confidence}%</span>
                </p>
              </motion.div>
            ) : (
              <motion.div
                key="no-data"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col items-center text-center py-4"
              >
                <div className="relative flex items-center justify-center mb-6 w-40 h-40">
                  <svg className="absolute inset-0 w-full h-full transform -rotate-90">
                    <circle
                      cx="80"
                      cy="80"
                      r={radius}
                      stroke="rgba(255,255,255,0.05)"
                      strokeWidth="6"
                      fill="transparent"
                    />
                  </svg>
                  <span className="text-7xl relative z-10 block leading-none pt-2 opacity-50 grayscale">🔍</span>
                </div>
                <p className="text-slate-400 font-mono tracking-widest uppercase text-sm">
                  {isStreaming ? 'Scanning...' : 'Camera Offline'}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Face count */}
        <div className="w-full flex items-center justify-center gap-2 mt-4 pt-4 border-t border-white/5">
          <Users className="w-4 h-4 text-slate-400" />
          <span className="text-sm text-slate-400 font-mono font-medium tracking-wide">
            Faces Detected: <span className="text-white font-bold">{isStreaming ? faceCount : 0}</span>
          </span>
        </div>
      </div>

      {/* 2. Detailed Metrics Panel (Bottom) */}
      <div className="glass-card p-6 flex-1 flex flex-col justify-center">
        <EmotionBars emotions={emotions} />
      </div>
    </motion.aside>
  );
}
