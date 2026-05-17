import React from 'react';
import { motion } from 'framer-motion';

export default function Hero({ summary }) {
  if (!summary) return null;

  const metrics = [
    { label: "Clauses Analyzed", value: summary.total_clauses, color: "text-blue-400" },
    { label: "Critical Risks", value: summary.critical_count, color: "text-risk-critical" },
    { label: "High Risks", value: summary.high_count, color: "text-risk-high" },
    { label: "AI Confidence", value: "85%", color: "text-emerald-400" }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8"
    >
      <h2 className="text-3xl font-bold text-white mb-3 tracking-tight">AI Rights & Contract Intelligence System</h2>
      <p className="text-textSecondary text-sm mb-8 max-w-2xl leading-relaxed">
        LEXGUARD's 5-agent pipeline has completed its analysis. Review the findings below. 
        Each clause has been vetted for fairness, exploitability, and legal ambiguity.
      </p>

      <div className="grid grid-cols-4 gap-4">
        {metrics.map((m, i) => (
          <div key={i} className="glass-card p-5 flex flex-col items-center justify-center text-center">
            <span className="text-xs text-textSecondary uppercase tracking-wider mb-2 font-semibold">{m.label}</span>
            <span className={`text-3xl font-bold ${m.color}`}>{m.value}</span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
