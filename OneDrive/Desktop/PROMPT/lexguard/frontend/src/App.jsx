import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText } from 'lucide-react';
import Sidebar from './components/Sidebar';
import ClauseCard from './components/ClauseCard';
import ActiveAnalysis from './components/ActiveAnalysis';
import RightPanel from './components/RightPanel';
import UploadModal from './components/UploadModal';

const API_BASE = window.location.hostname === 'localhost' && window.location.port === '5173' 
  ? 'http://localhost:8000' 
  : '';

function App() {
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeClause, setActiveClause] = useState(null);
  const [uploadOpen, setUploadOpen] = useState(false);

  // Auto-select highest risk clause on load
  useEffect(() => {
    if (result && result.clauses && result.clauses.length > 0) {
      const highest = result.clauses.find(c => c.risk_level === 'CRITICAL') ||
                      result.clauses.find(c => c.risk_level === 'HIGH') ||
                      result.clauses[0];
      setActiveClause(highest);
    }
  }, [result]);

  const handleAnalyze = async () => {
    if (!inputText.trim()) return;
    setLoading(true);
    setResult(null);
    setActiveClause(null);
    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Analysis failed');
      }
      const data = await res.json();
      setResult(data);
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = async () => {
    setLoading(true);
    setResult(null);
    setActiveClause(null);
    try {
      const res = await fetch(`${API_BASE}/demo`);
      if (!res.ok) throw new Error('Demo failed');
      const data = await res.json();
      setResult(data);
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#0A0A10] overflow-hidden text-[#F9FAFB] font-sans selection:bg-accent selection:text-white">
      
      {/* Background Gradients & Grid */}
      <div className="fixed inset-0 pointer-events-none z-0" style={{ backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />
      <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-accent/10 blur-[150px] pointer-events-none" />
      <div className="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500/5 blur-[150px] pointer-events-none" />

      {/* Upload Modal */}
      <UploadModal 
        isOpen={uploadOpen} 
        onClose={() => setUploadOpen(false)}
        inputText={inputText}
        setInputText={setInputText}
        onAnalyze={handleAnalyze}
        onDemo={handleDemo}
        loading={loading}
      />

      {/* Left Sidebar */}
      <Sidebar onOpenUpload={() => setUploadOpen(true)} />

      {/* Main Content Area */}
      <main className="flex-1 flex overflow-hidden relative z-10 pl-8 pr-4 py-8">
        <AnimatePresence mode="wait">
          {loading ? (
            <motion.div 
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex-1 flex flex-col items-center justify-center text-accent"
            >
              <div className="w-16 h-16 border-4 border-accent/20 border-t-accent rounded-full animate-spin mb-6 shadow-[0_0_30px_rgba(139,92,246,0.3)]" />
              <h2 className="text-xl font-bold text-white mb-2 tracking-widest uppercase">Running Convergence Engine</h2>
              <p className="text-gray-500 flex gap-4 text-xs mt-4 font-bold tracking-widest uppercase">
                <span className="animate-pulse">⚖️ Judge</span>
                <span className="animate-pulse delay-75">🔍 Adversarial</span>
                <span className="animate-pulse delay-150">💰 Financial</span>
              </p>
            </motion.div>
          ) : result ? (
            <motion.div 
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex-1 flex gap-8 h-full"
            >
              {/* Center Column: Active Analysis + Clause List */}
              <div className="flex-1 flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-4 pb-10">
                <ActiveAnalysis activeClause={activeClause} />
                
                <div className="flex flex-col gap-4 mt-4">
                  {result.clauses.map((clause, i) => (
                    <ClauseCard 
                      key={clause.clause_id} 
                      clause={clause} 
                      index={i} 
                      isActive={activeClause?.clause_id === clause.clause_id}
                      onSelect={setActiveClause}
                    />
                  ))}
                </div>
              </div>

              {/* Right Sidebar: Trust DNA + Copilot */}
              <RightPanel summary={result.document_summary} activeClause={activeClause} />
              
            </motion.div>
          ) : (
            <motion.div 
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex-1 flex flex-col items-center justify-center text-gray-500"
            >
              <div className="w-24 h-24 bg-white/5 rounded-3xl flex items-center justify-center mb-6 shadow-2xl border border-white/5 text-gray-600">
                <FileText className="w-10 h-10" />
              </div>
              <h2 className="text-lg font-bold text-gray-400 mb-3 tracking-widest uppercase">Awaiting Contract</h2>
              <p className="max-w-md text-center text-sm leading-relaxed text-gray-500">
                Click Upload Document in the Command Center to engage the multi-agent legal intelligence pipeline.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;

