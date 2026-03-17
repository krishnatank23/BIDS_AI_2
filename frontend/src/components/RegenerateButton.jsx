import { useState } from 'react';

/**
 * RegenerateButton – captures user feedback and triggers regeneration.
 */
export default function RegenerateButton({ agentName, onRegenerate, loading }) {
  const [feedback, setFeedback] = useState('');
  const [showInput, setShowInput] = useState(false);

  const handleSubmit = () => {
    if (feedback.trim().length < 3) return;
    onRegenerate(agentName, feedback.trim());
    setFeedback('');
    setShowInput(false);
  };

  return (
    <div className="space-y-3" id={`regenerate-${agentName}`}>
      {!showInput ? (
        <button
          onClick={() => setShowInput(true)}
          disabled={loading}
          className="btn-secondary text-sm flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Regenerate
        </button>
      ) : (
        <div className="space-y-2 animate-fade-in">
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder='e.g. "make it more premium" or "use darker colors"'
            rows={2}
            className="input-field text-sm resize-none"
          />
          <div className="flex gap-2">
            <button
              onClick={handleSubmit}
              disabled={loading || feedback.trim().length < 3}
              className="btn-primary text-sm flex items-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Regenerating...
                </>
              ) : (
                'Submit Feedback'
              )}
            </button>
            <button
              onClick={() => { setShowInput(false); setFeedback(''); }}
              className="btn-secondary text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
