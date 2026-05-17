import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Info, AlertTriangle, ExternalLink } from 'lucide-react';

export default function ActiveAnalysis({ activeClause }) {
  if (!activeClause) return null;

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={activeClause.clause_id}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        className="w-full bg-[#11111A] rounded-3xl border border-white/5 p-8 flex flex-col gap-8 shadow-2xl relative overflow-hidden"
      >
        {/* Subtle background glow based on risk */}
        <div className={`absolute top-0 right-0 w-96 h-96 rounded-full blur-[100px] opacity-10 pointer-events-none ${
          activeClause.risk_level === 'CRITICAL' ? 'bg-red-500' :
          activeClause.risk_level === 'HIGH' ? 'bg-orange-500' :
          activeClause.risk_level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'
        }`} />

        <div className="flex flex-col md:flex-row gap-8 relative z-10">
          
          {/* Why It Matters */}
          <div className="flex-1 flex flex-col gap-4">
            <div className="flex items-center gap-2 text-gray-400">
              <Info className="w-4 h-4" />
              <h3 className="text-xs font-bold uppercase tracking-widest">Why It Matters</h3>
            </div>
            <p className="text-gray-300 leading-relaxed text-sm md:text-base">
              {activeClause.why_it_matters || activeClause.plain_english}
            </p>
          </div>

          {/* System Threat (Worst Case) */}
          <div className="flex-1 flex flex-col gap-4">
            <div className="flex items-center gap-2 text-risk-high">
              <AlertTriangle className="w-4 h-4" />
              <h3 className="text-xs font-bold uppercase tracking-widest">! System Threat</h3>
            </div>
            <p className="text-gray-300 leading-relaxed text-sm md:text-base">
              {activeClause.future_scenarios?.worst_case || "No immediate system threat identified. Standard operational risks apply."}
            </p>
          </div>

        </div>

        {/* Footer Metrics */}
        <div className="pt-6 border-t border-white/5 flex flex-wrap items-center gap-x-12 gap-y-4 relative z-10">
          
          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">AI Consensus:</span>
            <div className="flex items-center gap-2">
              <span className={`text-sm font-bold tracking-wider ${
                activeClause.risk_level === 'CRITICAL' ? 'text-risk-critical' :
                activeClause.risk_level === 'HIGH' ? 'text-risk-high' :
                'text-accent'
              }`}>
                {activeClause.risk_level === 'CRITICAL' || activeClause.risk_level === 'HIGH' ? 'REJECT' : 'ACCEPT'} 
                <span className="opacity-80 ml-1">({(activeClause.confidence_score * 100).toFixed(0)}% CONFIDENCE)</span>
              </span>
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-[10px] font-bold text-gray-500 uppercase tracking-widest">Industry Risk:</span>
            <span className="text-sm font-bold text-white tracking-wider">
              {activeClause.risk_level === 'CRITICAL' ? 'TOP 0.5% VOLATILITY' :
               activeClause.risk_level === 'HIGH' ? 'TOP 5% VOLATILITY' :
               activeClause.risk_level === 'MEDIUM' ? 'STANDARD DEVIATION' : 'BASELINE'}
            </span>
          </div>

          <button className="ml-auto flex items-center gap-2 text-xs font-bold text-gray-400 hover:text-white transition-colors tracking-widest uppercase">
            Open Detailed Protocol <ExternalLink className="w-3 h-3" />
          </button>

        </div>
      </motion.div>
    </AnimatePresence>
  );
}
