import React from 'react';
import { LayoutGrid, BrainCircuit, Activity, Network, ShieldCheck } from 'lucide-react';

export default function Sidebar({ onOpenUpload }) {
  return (
    <aside className="w-64 bg-[#0A0A10] border-r border-white/5 flex flex-col h-full shrink-0 z-20 py-8 relative">
      <div className="px-8 flex flex-col gap-8 flex-1">
        
        {/* Navigation */}
        <nav className="flex flex-col gap-2">
          <button className="flex items-center gap-4 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white text-xs font-bold tracking-widest uppercase transition-all">
            <LayoutGrid className="w-4 h-4 text-accent" />
            Command Center
          </button>
          <button className="flex items-center gap-4 px-4 py-3 text-gray-500 hover:text-gray-300 hover:bg-white/[0.02] rounded-lg text-xs font-bold tracking-widest uppercase transition-all">
            <BrainCircuit className="w-4 h-4" />
            Legal Intel
          </button>
          <button className="flex items-center gap-4 px-4 py-3 text-gray-500 hover:text-gray-300 hover:bg-white/[0.02] rounded-lg text-xs font-bold tracking-widest uppercase transition-all">
            <Activity className="w-4 h-4" />
            Risk DNA
          </button>
          <button className="flex items-center gap-4 px-4 py-3 text-gray-500 hover:text-gray-300 hover:bg-white/[0.02] rounded-lg text-xs font-bold tracking-widest uppercase transition-all">
            <Network className="w-4 h-4" />
            Nexus Assets
          </button>
          <button className="flex items-center gap-4 px-4 py-3 text-gray-500 hover:text-gray-300 hover:bg-white/[0.02] rounded-lg text-xs font-bold tracking-widest uppercase transition-all">
            <ShieldCheck className="w-4 h-4" />
            Protocols
          </button>
        </nav>
      </div>

      {/* Bottom Actions */}
      <div className="px-8 mt-auto flex flex-col gap-6">
        <button
          onClick={onOpenUpload}
          className="w-full py-4 bg-accent hover:bg-accentAlt text-white font-bold text-xs uppercase tracking-widest rounded-xl transition-all shadow-[0_0_20px_rgba(139,92,246,0.3)]"
        >
          Upload Document
        </button>

        <div className="flex items-center justify-between border-t border-white/10 pt-6">
          <div className="flex items-center gap-2 text-gray-500">
            <ShieldCheck className="w-4 h-4" />
            <span className="text-[10px] font-bold uppercase tracking-widest">Secure</span>
          </div>
          <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">L3</span>
        </div>
      </div>
    </aside>
  );
}
