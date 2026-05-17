import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquareText, FileLock2 } from 'lucide-react';

const CircularProgress = ({ value, label, text }) => {
  const radius = 35;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative w-24 h-24 flex items-center justify-center">
        {/* Background circle */}
        <svg className="w-full h-full transform -rotate-90">
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke="currentColor"
            strokeWidth="6"
            fill="transparent"
            className="text-white/10"
          />
          {/* Progress circle */}
          <circle
            cx="48"
            cy="48"
            r={radius}
            stroke="currentColor"
            strokeWidth="6"
            fill="transparent"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.5)] transition-all duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold text-white tracking-wider">{text}</span>
        </div>
      </div>
      <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">{label}</span>
    </div>
  );
};

export default function RightPanel({ summary, activeClause }) {
  const fairnessScore = summary?.trust_dna?.fairness || 0;
  const transparencyScore = summary?.trust_dna?.transparency || 0;

  // Convert A+ scale if needed, for visual we just use the raw score for circumference but render the label
  const getGrade = (score) => {
    if (score >= 90) return 'A+';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B';
    if (score >= 60) return 'C';
    if (score >= 50) return 'D';
    return 'F';
  };

  return (
    <div className="w-[380px] shrink-0 flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-2 pb-10">
      
      {/* Trust DNA */}
      {summary && (
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex flex-col gap-4"
        >
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 rounded-full bg-white/40" />
            <h2 className="text-xs font-bold text-gray-400 uppercase tracking-[0.2em]">Enterprise Trust DNA</h2>
          </div>
          
          <div className="flex justify-around items-center bg-[#11111A] p-6 rounded-2xl border border-white/5">
            <CircularProgress 
              value={fairnessScore} 
              label="Fairness" 
              text={getGrade(fairnessScore)} 
            />
            <CircularProgress 
              value={transparencyScore} 
              label="Transparency" 
              text={`${transparencyScore}%`} 
            />
          </div>
        </motion.div>
      )}

      {/* AI Negotiation Copilot */}
      <AnimatePresence mode="wait">
        {activeClause && activeClause.negotiation_tip && (
          <motion.div
            key={activeClause.clause_id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex flex-col flex-1"
          >
            <div className="bg-[#11111A] rounded-2xl border border-accent/20 overflow-hidden flex flex-col shadow-[0_0_30px_rgba(139,92,246,0.1)]">
              
              <div className="p-5 border-b border-white/5 flex items-center gap-3 bg-white/[0.02]">
                <MessageSquareText className="w-5 h-5 text-accent" />
                <h3 className="text-sm font-bold text-gray-300 uppercase tracking-widest">AI Negotiation Copilot</h3>
              </div>

              <div className="p-6 flex flex-col gap-6">
                <p className="text-sm text-gray-400 italic leading-relaxed">
                  "{activeClause.negotiation_tip}"
                </p>

                <div className="flex flex-col gap-3">
                  <h4 className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Optimized Rewrite Recommendation</h4>
                  
                  {/* Original text mockup - typically strikethrough */}
                  <div className="bg-black/30 rounded-xl p-4 border border-white/5 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-1 h-full bg-red-500/50" />
                    <p className="text-sm text-gray-500 font-mono line-through opacity-70">
                      "...{activeClause.title.toLowerCase()} as stated..."
                    </p>
                  </div>

                  {/* Rewrite suggestion */}
                  <div className="bg-accent/5 rounded-xl p-4 border border-accent/20 relative overflow-hidden shadow-[inset_0_0_20px_rgba(139,92,246,0.05)]">
                    <div className="absolute top-0 left-0 w-1 h-full bg-accent" />
                    <p className="text-sm text-accent font-mono leading-relaxed">
                      "{activeClause.suggested_rewrite}"
                    </p>
                  </div>
                </div>

                <button className="mt-2 w-full py-3.5 bg-accent/10 hover:bg-accent hover:text-white text-accent transition-all duration-300 rounded-xl font-bold text-xs uppercase tracking-wider border border-accent/30 flex items-center justify-center gap-2">
                  <FileLock2 className="w-4 h-4" />
                  Apply & Synchronize Modification
                </button>
              </div>

            </div>
          </motion.div>
        )}
      </AnimatePresence>

    </div>
  );
}
