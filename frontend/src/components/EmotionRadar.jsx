/**
 * EmotionRadar — Recharts RadarChart for emotion probability visualization
 */
import { RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';
import { motion } from 'framer-motion';

const EMOTIONS_ORDER = ['happy', 'sad', 'angry', 'surprise', 'fear', 'disgust', 'neutral'];

const EMOTION_LABELS = {
  happy: 'Happy',
  sad: 'Sad',
  angry: 'Angry',
  surprise: 'Surprise',
  fear: 'Fear',
  disgust: 'Disgust',
  neutral: 'Neutral',
};

export default function EmotionRadar({ emotions }) {
  const data = EMOTIONS_ORDER.map((key) => ({
    emotion: EMOTION_LABELS[key],
    value: emotions?.[key] ? Math.round(emotions[key] * 100) / 100 : 0,
    fullMark: 100,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full"
    >
      <h3 className="text-xs font-mono text-slate-500 tracking-widest uppercase mb-3 px-1">
        Emotion Radar
      </h3>
      <div className="w-full" style={{ height: 240 }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="72%" data={data}>
            <PolarGrid 
              stroke="rgba(0, 240, 255, 0.08)" 
              strokeDasharray="3 3"
            />
            <PolarAngleAxis 
              dataKey="emotion" 
              tick={{ fill: '#94a3b8', fontSize: 10, fontFamily: 'Inter' }}
            />
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 100]} 
              tick={false}
              axisLine={false}
            />
            <Radar
              name="Confidence"
              dataKey="value"
              stroke="#00f0ff"
              strokeWidth={2}
              fill="url(#radarGradient)"
              fillOpacity={0.4}
              isAnimationActive={false}
            />
            <defs>
              <linearGradient id="radarGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#00f0ff" stopOpacity={0.6} />
                <stop offset="100%" stopColor="#a855f7" stopOpacity={0.2} />
              </linearGradient>
            </defs>
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
