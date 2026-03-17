export default function ProgressTimeline({ agents, labels, completed, expandedAgent, onExpandAgent }) {
  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-4 -mx-6 px-6">
      {agents.map((agentName, index) => {
        const isDone = completed.includes(agentName);
        const meta = labels[agentName];
        const isLast = index === agents.length - 1;

        return (
          <div key={agentName} className="flex items-center gap-2 flex-shrink-0">
            {/* Agent circle */}
            <button
              onClick={() => onExpandAgent(expandedAgent === agentName ? null : agentName)}
              className={`relative w-14 h-14 rounded-full flex items-center justify-center font-semibold text-lg transition-all duration-300 flex-shrink-0 ${
                isDone
                  ? `bg-gradient-to-br ${meta.color} text-white shadow-lg shadow-${meta.color.split('-')[1]}-500/30 hover:shadow-xl`
                  : 'bg-white/5 text-white/40 border border-white/10 hover:bg-white/10'
              }`}
              title={meta.label}
            >
              {meta.icon}
              {isDone && (
                <div className="absolute inset-0 rounded-full bg-white/20 animate-pulse" />
              )}
            </button>

            {/* Connector line */}
            {!isLast && (
              <div className="w-6 h-1 rounded-full flex-shrink-0 bg-white/5" />
            )}
          </div>
        );
      })}
    </div>
  );
}
