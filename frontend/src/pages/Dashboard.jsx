import { useState, useEffect, useCallback } from 'react';
import AgentCard from '../components/AgentCard';
import LogoViewer from '../components/LogoViewer';
import ProgressTimeline from '../components/ProgressTimeline';
import { runNextStep, runFullWorkflow, getProject, regenerate } from '../services/api';

const AGENT_ORDER = [
  'idea_discovery', 'market_research', 'competitor_analysis', 'brand_strategy', 'naming',
  'design_agent', 'logo_generator', 'content_agent', 'guidelines_agent', 'export_agent',
];

const STEP_LABELS = {
  idea_discovery: { icon: '💡', label: 'Idea Analysis', color: 'from-blue-500 to-blue-600' },
  market_research: { icon: '📊', label: 'Market Research', color: 'from-purple-500 to-purple-600' },
  competitor_analysis: { icon: '🔍', label: 'Competitor Analysis', color: 'from-pink-500 to-pink-600' },
  brand_strategy: { icon: '🎯', label: 'Brand Strategy', color: 'from-red-500 to-red-600' },
  naming: { icon: '✏️', label: 'Brand Naming', color: 'from-orange-500 to-orange-600' },
  design_agent: { icon: '🎨', label: 'Design Direction', color: 'from-yellow-500 to-yellow-600' },
  logo_generator: { icon: '🖼️', label: 'Logo Output', color: 'from-green-500 to-green-600' },
  content_agent: { icon: '📝', label: 'Content', color: 'from-teal-500 to-teal-600' },
  guidelines_agent: { icon: '📋', label: 'Guidelines', color: 'from-cyan-500 to-cyan-600' },
  export_agent: { icon: '📦', label: 'Export', color: 'from-indigo-500 to-indigo-600' },
};

export default function Dashboard({ project, onBack }) {
  const [agentOutputs, setAgentOutputs] = useState({});
  const [status, setStatus] = useState(project?.status || 'created');
  const [loading, setLoading] = useState(false);
  const [runningAll, setRunningAll] = useState(false);
  const [error, setError] = useState('');
  const [expandedAgent, setExpandedAgent] = useState(null);

  // ✅ Ensure project ID is valid string
  const projectId = project?.id?.toString?.() || project?.id;

  const fetchState = useCallback(async () => {
    if (!projectId) {
      setError('No project ID available');
      return;
    }
    try {
      const res = await getProject(projectId);
      setAgentOutputs(res.data?.agent_outputs || {});
      setStatus(res.data?.project?.status || 'created');
      setError(''); // Clear error on success
    } catch (err) {
      console.error('Failed to fetch project state:', err);
      setError(err.response?.data?.detail || 'Failed to fetch project state');
    }
  }, [projectId]);

  useEffect(() => {
    fetchState();
  }, [fetchState]);

  // ✅ NEW: Poll for progress while workflow is running
  useEffect(() => {
    if (status !== 'running') return;

    const pollInterval = setInterval(async () => {
      await fetchState();
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [status, fetchState]);

  const handleNextStep = async () => {
    setLoading(true);
    setError('');
    try {
      if (!projectId) {
        throw new Error('No project ID');
      }
      const res = await runNextStep(projectId);
      setStatus(res.data?.status || 'running');
      // Start immediate polling
      setTimeout(() => fetchState(), 500);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Step execution failed';
      setError(errorMsg);
      console.error('Step error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAll = async () => {
    setRunningAll(true);
    setError('');
    try {
      if (!projectId) {
        throw new Error('No project ID');
      }
      const res = await runFullWorkflow(projectId);
      setStatus(res.data?.status || 'running');
      // Start immediate polling
      setTimeout(() => fetchState(), 500);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Workflow failed';
      setError(errorMsg);
      console.error('Workflow error:', err);
    } finally {
      setRunningAll(false);
    }
  };

  const handleRegenerate = async (agentName, feedback = '') => {
    try {
      setError('');
      if (!projectId) {
        throw new Error('No project ID');
      }
      await regenerate(projectId, agentName, feedback);
      await fetchState();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Regeneration failed';
      setError(errorMsg);
      console.error('Regenerate error:', err);
    }
  };

  const completedAgents = Object.keys(agentOutputs);
  const progress = (completedAgents.length / AGENT_ORDER.length) * 100;
  const isComplete = status === 'completed';

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 space-y-12 min-h-screen">
      {/* Top Navigation & Status */}
      <div className="flex items-center justify-between animate-fade-in">
        <button 
          onClick={onBack} 
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white/80 hover:text-white transition-all"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Home
        </button>
        <span className={`px-4 py-2 rounded-full font-semibold text-sm ${
          isComplete 
            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' 
            : status === 'running' 
            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' 
            : 'bg-white/10 text-white/60 border border-white/10'
        }`}>
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Project Info Card */}
      <div className="relative group animate-slide-up">
        <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-500" />
        <div className="relative bg-slate-950/80 backdrop-blur-xl rounded-2xl p-8 space-y-8 border border-white/10">
          <div>
            <h1 className="text-3xl font-black bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-3 uppercase tracking-tight">
              Brand Identity Project
            </h1>
            <p className="text-xl text-white/70 leading-relaxed font-medium">{project?.idea || 'Loading...'}</p>
            <div className="flex items-center gap-4 mt-6 text-xs text-white/30">
              <span>ID: <span className="font-mono text-white/50">{projectId}</span></span>
              <span>•</span>
              <span>Created: {project?.created_at ? new Date(project.created_at).toLocaleString() : 'N/A'}</span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="space-y-4">
            <div className="flex justify-between items-end">
              <span className="text-sm font-bold text-white/50 uppercase tracking-widest">Pipeline Status</span>
              <span className="text-2xl font-black text-white">{Math.round(progress)}%</span>
            </div>
            <div className="relative h-4 bg-white/5 rounded-full overflow-hidden border border-white/10 p-0.5">
              <div 
                className="h-full bg-gradient-to-r from-blue-600 via-blue-400 to-cyan-400 rounded-full transition-all duration-1000 cubic-bezier(0.4, 0, 0.2, 1)" 
                style={{ width: `${progress}%` }} 
              />
            </div>
            <div className="flex justify-between text-[10px] text-white/40 font-mono uppercase tracking-widest">
              <span>Initialized</span>
              <span>{completedAgents.length} Agents Completed</span>
              <span>Brand Ready</span>
            </div>
          </div>

          {/* Controls */}
          {!isComplete && (
            <div className="flex flex-wrap gap-4 pt-4 border-t border-white/5">
              <button 
                onClick={handleNextStep} 
                disabled={loading || runningAll} 
                className="flex-1 min-w-[180px] flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-500/20 active:scale-95"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Executing...</span>
                  </>
                ) : (
                  <>
                    <span className="text-xl">▶</span>
                    <span>NEXT STEP</span>
                  </>
                )}
              </button>
              <button 
                onClick={handleRunAll} 
                disabled={loading || runningAll} 
                className="flex-1 min-w-[180px] flex items-center justify-center gap-3 px-8 py-4 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 text-white font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
              >
                {runningAll ? (
                  <>
                    <div className="w-5 h-5 border-3 border-white/30 border-t-white rounded-full animate-spin" />
                    <span>Processing All...</span>
                  </>
                ) : (
                  <>
                    <span className="text-xl">⚡</span>
                    <span>RUN FULL PIPELINE</span>
                  </>
                )}
              </button>
            </div>
          )}

          {isComplete && (
            <div className="p-6 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-5 animate-fade-in-up">
              <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center text-2xl">✅</div>
              <div>
                <h4 className="font-black text-emerald-400 uppercase tracking-tight">Generation Successful</h4>
                <p className="text-sm text-emerald-300/70">Your complete brand ecosystem is now persistent and ready for deployment.</p>
              </div>
            </div>
          )}

          {error && (
            <div className="p-6 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-4 animate-shake">
              <span className="text-2xl mt-1">⚠️</span>
              <div>
                <h4 className="font-bold text-red-400 uppercase tracking-tight text-sm">System Error</h4>
                <p className="text-sm text-red-300/70">{error}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Progress Timeline View */}
      <div className="space-y-8">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Workflow Pipeline</h2>
          <div className="h-px flex-1 bg-white/5" />
        </div>
        <ProgressTimeline 
          agents={AGENT_ORDER} 
          labels={STEP_LABELS} 
          completed={completedAgents} 
          expandedAgent={expandedAgent} 
          onExpandAgent={setExpandedAgent} 
        />
      </div>

      {/* Agent Output Grid */}
      <div className="space-y-8">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-black text-white uppercase tracking-tighter">Identity Generation</h2>
          <div className="h-px flex-1 bg-white/5" />
        </div>
        
        {completedAgents.length === 0 ? (
          <div className="text-center py-24 rounded-3xl bg-white/2 border border-dashed border-white/10 animate-pulse-slow">
            <div className="text-6xl mb-6">🛰️</div>
            <h3 className="text-xl font-bold text-white/60 mb-2 uppercase">Awaiting Activation</h3>
            <p className="text-white/30 max-w-sm mx-auto text-sm">Initialize the pipeline to start receiving neural outputs from the agent swarm.</p>
          </div>
        ) : (
          <div className="grid gap-8">
            {AGENT_ORDER.map((agentName) => {
              const output = agentOutputs[agentName];
              if (!output) return null;

              return (
                <div key={agentName} className="space-y-6 animate-slide-up">
                  <AgentCard 
                    agentName={agentName} 
                    output={output} 
                    onRegenerate={handleRegenerate}
                    isExpanded={expandedAgent === agentName}
                    onToggle={() => setExpandedAgent(expandedAgent === agentName ? null : agentName)}
                  />
                  {/* Logo Variations Viewer */}
                  {agentName === 'logo_generator' && output.output_json && (
                    <div className="animate-fade-in">
                      <LogoViewer logoData={output.output_json} onRegenerate={handleRegenerate} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Final Export View */}
      {isComplete && agentOutputs.export_agent && (
        <div className="relative group py-12 pt-0">
          <div className="absolute -inset-1 bg-gradient-to-r from-emerald-500 via-cyan-500 to-blue-500 rounded-3xl blur opacity-25 group-hover:opacity-40 transition duration-500" />
          <div className="relative bg-slate-950 rounded-3xl p-12 text-center space-y-8 border border-white/10">
            <div className="flex justify-center">
              <div className="w-24 h-24 rounded-full bg-emerald-500/10 flex items-center justify-center text-5xl animate-bounce">📦</div>
            </div>
            <div>
              <h2 className="text-4xl font-black text-white uppercase tracking-tighter">Brand Distribution Ready</h2>
              <p className="text-white/50 max-w-2xl mx-auto mt-4 leading-relaxed">
                Your brand architecture has been fully compiled into high-fidelity documents. 
                Download your comprehensive brand kit across multiple formats.
              </p>
            </div>
            
            <div className="flex justify-center gap-4 flex-wrap pt-4">
              {agentOutputs.export_agent?.output_json?.pdf_path && (
                <a 
                  href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/exports/${agentOutputs.export_agent.output_json.pdf_path.split('/').pop()}`} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="group flex items-center gap-4 px-10 py-5 rounded-2xl bg-white text-slate-950 font-black transition-all hover:scale-105 active:scale-95 shadow-xl shadow-white/10"
                >
                  <span className="text-2xl">📄</span>
                  <div className="text-left">
                    <div className="text-[10px] uppercase opacity-50 tracking-widest">Format</div>
                    <div>DOWNLOAD PDF</div>
                  </div>
                </a>
              )}
              {agentOutputs.export_agent?.output_json?.docx_path && (
                <a 
                  href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/exports/${agentOutputs.export_agent.output_json.docx_path.split('/').pop()}`} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="group flex items-center gap-4 px-10 py-5 rounded-2xl bg-white/5 hover:bg-white/10 border border-white/20 text-white font-black transition-all hover:scale-105 active:scale-95"
                >
                  <span className="text-2xl">📝</span>
                  <div className="text-left">
                    <div className="text-[10px] uppercase opacity-50 tracking-widest">Format</div>
                    <div>DOWNLOAD DOCX</div>
                  </div>
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
