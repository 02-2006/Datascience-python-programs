import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, FileText } from 'lucide-react';

export default function UploadModal({ isOpen, onClose, inputText, setInputText, onAnalyze, onDemo, loading }) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            exit={{ scale: 0.95, opacity: 0, y: 20 }}
            className="w-full max-w-2xl bg-[#11111A] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col"
          >
            <div className="p-6 border-b border-white/10 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-accent" />
                Upload Contract
              </h2>
              <button 
                onClick={onClose}
                className="p-2 hover:bg-white/5 rounded-lg text-gray-400 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 flex flex-col gap-4">
              <p className="text-sm text-gray-400">
                Paste your legal contract text below for the multi-agent legal intelligence pipeline to analyze.
              </p>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Paste contract text here..."
                className="w-full h-64 bg-black/40 border border-white/10 rounded-xl p-4 text-sm text-gray-300 font-mono focus:outline-none focus:border-accent/50 transition-colors resize-none custom-scrollbar"
              />
            </div>

            <div className="p-6 border-t border-white/10 flex gap-4 bg-black/20 justify-end">
              <button
                onClick={() => {
                  onDemo();
                  onClose();
                }}
                disabled={loading}
                className="px-6 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-medium rounded-lg transition-all disabled:opacity-50"
              >
                Load Demo Contract
              </button>
              <button
                onClick={() => {
                  onAnalyze();
                  if (inputText.trim()) onClose();
                }}
                disabled={loading || !inputText.trim()}
                className="px-6 py-2.5 bg-accent hover:bg-blue-500 text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-accent/20"
              >
                {loading ? 'Analyzing...' : 'Run Analysis'}
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
