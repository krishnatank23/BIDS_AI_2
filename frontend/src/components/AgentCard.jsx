import { useState } from 'react';
import ColorPalette from './ColorPalette';

const AGENT_META = {
  idea_discovery:      { icon: '💡', label: 'Idea Discovery' },
  market_research:     { icon: '📊', label: 'Market Research' },
  competitor_analysis: { icon: '🔍', label: 'Competitor Analysis' },
  brand_strategy:      { icon: '🎯', label: 'Brand Strategy' },
  naming:              { icon: '✏️', label: 'Brand Naming' },
  design_agent:        { icon: '🎨', label: 'Design Direction' },
  logo_generator:      { icon: '🖼️', label: 'Logo Output' },
  content_agent:       { icon: '📝', label: 'Brand Content' },
  guidelines_agent:    { icon: '📋', label: 'Brand Guidelines' },
  export_agent:        { icon: '📦', label: 'Export & Download' },
};

function JsonTree({ data, depth = 0 }) {
  if (data === null || data === undefined) return <span className="text-white/30">—</span>;

  if (typeof data === 'string') {
    return <span className="text-emerald-300 break-words">{data}</span>;
  }
  if (typeof data === 'number' || typeof data === 'boolean') {
    return <span className="text-amber-300">{String(data)}</span>;
  }

  if (Array.isArray(data)) {
    return (
      <ul className="space-y-1 pl-4 border-l border-white/5">
        {data.map((item, i) => (
          <li key={i} className="text-sm">
            <span className="text-blue-400 mr-2">•</span>
            <JsonTree data={item} depth={depth + 1} />
          </li>
        ))}
      </ul>
    );
  }

  if (typeof data === 'object') {
    return (
      <div className={`space-y-2 ${depth > 0 ? 'pl-4 border-l border-white/5' : ''}`}>
        {Object.entries(data).map(([key, value]) => {
          if (key === 'logo_base64') return null;
          return (
            <div key={key}>
              <span className="text-blue-400 font-medium text-sm capitalize">
                {key.replace(/_/g, ' ')}:
              </span>
              <div className="ml-2 mt-0.5">
                <JsonTree data={value} depth={depth + 1} />
              </div>
            </div>
          );
        })}
      </div>
    );
  }

  return <span>{String(data)}</span>;
}

export default function AgentCard({ agentName, output, onRegenerate, isExpanded, onToggle }) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');
  const [isRegenerating, setIsRegenerating] = useState(false);

  const meta = AGENT_META[agentName] || { icon: '🤖', label: agentName };
  const canRegenerate = ['design_agent', 'logo_generator', 'content_agent'].includes(agentName);

  if (!output) return null;

  const { output_json, explanation, version, created_at } = output;

  const handleRegenerateClick = async () => {
    if (feedbackText.trim().length < 3) return;
    setIsRegenerating(true);
    try {
      await onRegenerate(agentName, feedbackText.trim());
      setShowFeedback(false);
      setFeedbackText('');
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="glass-card overflow-hidden transition-all duration-300 hover:border-blue-500/50" id={`agent-${agentName}`}>
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-6 text-left group hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-4 flex-1 min-w-0">
          <span className="text-3xl flex-shrink-0">{meta.icon}</span>
          <div className="min-w-0 flex-1">
            <h3 className="text-lg font-semibold text-white group-hover:text-blue-300 transition-colors">
              {meta.label}
            </h3>
            <p className="text-white/40 text-sm mt-0.5">
              v{version} • {new Date(created_at).toLocaleString()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0 ml-4">
          {canRegenerate && (
            <span className="px-2 py-1 text-[9px] font-black text-cyan-300 bg-cyan-500/10 border border-cyan-500/20 rounded-full font-mono uppercase tracking-widest">
              Swarm Iteration Available
            </span>
          )}
          <span className="px-3 py-1 text-[9px] font-black text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 rounded-full font-mono uppercase tracking-widest">
            Verified Output
          </span>
          <svg
            className={`w-5 h-5 text-white/40 transition-transform duration-300 flex-shrink-0 ${isExpanded ? 'rotate-180' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Expandable Content */}
      {isExpanded && (
        <div className="border-t border-white/5 animate-fade-in">
          {/* Explanation */}
          {explanation && (
            <div className="px-6 py-4 bg-blue-500/5 border-b border-white/5">
              <h4 className="text-[10px] font-black text-blue-400 uppercase tracking-[0.2em] mb-2 opacity-50">
                Strategic Summary
              </h4>
              <p className="text-white/70 text-sm leading-relaxed">{explanation}</p>
            </div>
          )}

          {/* Output Data */}
          <div className="px-6 py-4">
            <h4 className="text-[10px] font-black text-white/40 uppercase tracking-[0.2em] mb-4">
              Agent Structured Data
            </h4>
            <div className="bg-white/[0.02] rounded-2xl p-6 max-h-[500px] overflow-y-auto border border-white/5 shadow-inner">
              {agentName === 'design_agent' && output_json.color_palette && (
                <div className="mb-10">
                   <ColorPalette palette={output_json.color_palette} />
                </div>
              )}
              <JsonTree data={output_json} />
            </div>
          </div>

          {/* Regenerate Action Area */}
          {canRegenerate && onRegenerate && (
            <div className="px-6 py-6 border-t border-white/5 bg-white/[0.01]">
              {!showFeedback ? (
                <button
                  onClick={() => setShowFeedback(true)}
                  className="flex items-center gap-3 px-6 py-3 rounded-xl bg-blue-600/10 hover:bg-blue-600/20 border border-blue-600/30 hover:border-blue-600/50 text-blue-400 font-bold transition-all text-xs uppercase tracking-widest active:scale-95 group"
                >
                  <span className="text-lg group-hover:rotate-180 transition-transform duration-500">🔄</span>
                  <span>TRIGGER SWARM ITERATION</span>
                </button>
              ) : (
                <div className="space-y-4 animate-fade-in-up">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-white/30 uppercase tracking-[0.2em]">Feedback Loop</label>
                    <textarea
                      value={feedbackText}
                      onChange={(e) => setFeedbackText(e.target.value)}
                      placeholder='e.g. "make the colors more vibrant" or "it feels too corporate"'
                      rows={3}
                      className="w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl text-white placeholder-white/20 focus:outline-none focus:border-blue-500/50 transition-all font-medium text-sm resize-none"
                    />
                  </div>
                  <div className="flex gap-3">
                    <button
                      onClick={handleRegenerateClick}
                      disabled={isRegenerating || feedbackText.trim().length < 3}
                      className="flex-1 flex items-center justify-center gap-3 px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed text-xs uppercase tracking-widest"
                    >
                      {isRegenerating ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          <span>PROCESSING...</span>
                        </>
                      ) : (
                        <span>SUBMIT FEEDBACK</span>
                      )}
                    </button>
                    <button
                      onClick={() => { setShowFeedback(false); setFeedbackText(''); }}
                      className="px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white/60 font-bold transition-all text-xs uppercase tracking-widest"
                    >
                      CANCEL
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
