import React from 'react';
import { motion } from 'framer-motion';

export default function TrustGauge({ label, value }) {
  const getColor = (v) => {
    if (v > 70) return 'bg-risk-low';
    if (v > 40) return 'bg-risk-medium';
    return 'bg-risk-critical';
  };

  return (
    <div className="flex flex-col gap-1.5 mb-4">
      <div className="flex justify-between text-xs text-textSecondary font-medium">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="w-full h-1.5 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-full rounded-full ${getColor(value)}`}
        />
      </div>
    </div>
  );
}
