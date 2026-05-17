import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, AlertTriangle, BadgeInfo, CheckCircle2, Info, Lock, Briefcase, Ban, UserMinus, IndianRupee, Scale, User, FileText } from 'lucide-react';

export default function ClauseCard({ clause, index, isActive, onSelect }) {
  
  const getRiskColor = (level) => {
    switch (level) {
      case 'CRITICAL': return 'text-risk-critical border-risk-critical/30 bg-risk-critical/10';
      case 'HIGH': return 'text-risk-high border-risk-high/30 bg-risk-high/10';
      case 'MEDIUM': return 'text-risk-medium border-risk-medium/30 bg-risk-medium/10';
      case 'LOW': return 'text-risk-low border-risk-low/30 bg-risk-low/10';
      case 'INFORMATIONAL': return 'text-gray-400 border-gray-600/30 bg-gray-800/20';
      default: return 'text-textSecondary border-borderAlt bg-white/5';
    }
  };

  const getClauseTypeIcon = (type) => {
    switch (type) {
      case 'Intellectual Property': return <Lock className="w-5 h-5 text-gray-400" />;
      case 'Employment': return <Briefcase className="w-5 h-5 text-gray-400" />;
      case 'Non-Compete': return <Ban className="w-5 h-5 text-gray-400" />;
      case 'Termination': return <UserMinus className="w-5 h-5 text-gray-400" />;
      case 'Compensation': return <IndianRupee className="w-5 h-5 text-gray-400" />;
      case 'Arbitration': return <Scale className="w-5 h-5 text-gray-400" />;
      case 'Dispute Resolution': return <Scale className="w-5 h-5 text-gray-400" />;
      case 'Privacy': return <User className="w-5 h-5 text-gray-400" />;
      case 'Compliance': return <Info className="w-5 h-5 text-gray-400" />;
      default: return <FileText className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      onClick={() => onSelect(clause)}
      className={`relative p-6 flex flex-col gap-5 rounded-2xl border cursor-pointer transition-all duration-300 group
        ${isActive 
          ? 'bg-[#1A1A24] border-accent/50 shadow-[0_0_20px_rgba(139,92,246,0.15)]' 
          : 'bg-[#11111A] border-white/5 hover:border-white/20 hover:bg-[#15151F]'
        }
      `}
    >
      {/* Active Indicator Glow */}
      {isActive && (
        <div className="absolute inset-0 rounded-2xl shadow-[inset_0_0_20px_rgba(139,92,246,0.05)] pointer-events-none" />
      )}

      {/* Header */}
      <div className="flex items-start gap-4">
        <div className="p-3 bg-white/5 rounded-xl border border-white/10 shrink-0">
          {getClauseTypeIcon(clause.clause_type)}
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-start gap-2">
            <h3 className="text-lg font-bold text-white leading-tight">
              {clause.title}
            </h3>
            {/* Risk Badge */}
            <div className={`shrink-0 px-3 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest ${getRiskColor(clause.risk_level)}`}>
              {clause.risk_level === 'CRITICAL' ? 'WARNING: CRITICAL RISK' : 
               clause.risk_level === 'HIGH' ? 'WARNING: HIGH RISK' : 
               clause.risk_level === 'MEDIUM' ? 'WARNING: MEDIUM RISK' : 
               clause.risk_level === 'INFORMATIONAL' ? 'INFORMATIONAL' : 'LOW RISK'}
            </div>
          </div>
        </div>
      </div>

      {/* Excerpt */}
      <div className="pl-[60px]">
        <p className="text-sm text-gray-400 leading-relaxed line-clamp-3">
          {clause.plain_english}
        </p>
      </div>

      {/* Actions */}
      <div className="pl-[60px] flex items-center gap-4 mt-2">
        <button 
          className="px-4 py-2 bg-white/5 hover:bg-white/10 text-gray-300 text-[10px] font-bold uppercase tracking-widest rounded-lg transition-colors"
        >
          Modify Clause
        </button>
        <button 
          className="text-[10px] font-bold uppercase tracking-widest text-gray-500 hover:text-white transition-colors"
        >
          Deep Dive Analysis
        </button>
      </div>

    </motion.div>
  );
}
