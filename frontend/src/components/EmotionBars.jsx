/**
 * EmotionBars — Animated horizontal progress bars for each emotion
 */
import { motion } from 'framer-motion';

const EMOTIONS_CONFIG = [
  { key: 'happy',    label: 'Happy',    emoji: '😊' },
  { key: 'sad',      label: 'Sad',      emoji: '😢' },
  { key: 'angry',    label: 'Angry',    emoji: '😠' },
  { key: 'surprise', label: 'Surprise', emoji: '😲' },
  { key: 'fear',     label: 'Fear',     emoji: '😨' },
  { key: 'disgust',  label: 'Disgust',  emoji: '🤢' },
  { key: 'neutral',  label: 'Neutral',  emoji: '😐' },
];

export default function EmotionBars({ emotions }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      <h3 className="text-xs font-mono text-slate-500 tracking-widest uppercase mb-3 px-1">
        Confidence Scores
      </h3>
      <div className="space-y-2.5">
        {EMOTIONS_CONFIG.map((emotion, index) => {
          const value = emotions?.[emotion.key] ?? 0;
          const percentage = Math.round(value * 100) / 100;
          const isMax = emotions && Object.keys(emotions).length > 0 &&
            emotion.key === Object.entries(emotions).sort(([,a], [,b]) => b - a)[0]?.[0];

          return (
            <motion.div
              key={emotion.key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
              className={`relative rounded-sm p-2 transition-all duration-300 ${
                isMax ? 'bg-white/[0.03] ring-1 ring-accent-cyan/20' : ''
              }`}
            >
              {/* Label row */}
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-base">{emotion.emoji}</span>
                  <span className={`text-xs font-medium uppercase tracking-wider ${
                    isMax ? 'text-accent-cyan font-bold' : 'text-slate-400'
                  }`}>
                    {emotion.label}
                  </span>
                </div>
                <span className={`text-xs font-mono font-semibold ${
                  isMax ? 'text-accent-cyan' : 'text-slate-500'
                }`}>
                  {percentage.toFixed(1)}%
                </span>
              </div>

              {/* Progress bar */}
              <div className="h-1.5 rounded-sm overflow-hidden bg-surface-700/50">
                <motion.div
                  className="h-full rounded-sm bg-accent-cyan"
                  style={{
                    boxShadow: isMax ? `0 0 10px rgba(0, 240, 255, 0.6)` : 'none',
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(percentage, 100)}%` }}
                  transition={{ duration: 0.3, ease: 'easeOut' }}
                />
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}
