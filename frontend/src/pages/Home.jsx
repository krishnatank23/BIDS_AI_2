import { useState } from 'react';
import { createProject } from '../services/api';
import FeatureCard from '../components/FeatureCard';

export default function Home({ onProjectCreated }) {
  const [idea, setIdea] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (idea.trim().length < 5) {
      setError('Please describe your idea in at least 5 characters.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await createProject(idea.trim());
      setSubmitted(true);
      setTimeout(() => {
        onProjectCreated(res.data);
      }, 500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create project. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: '🎯',
      title: 'Brand Strategy',
      description: 'Comprehensive market analysis and positioning strategy'
    },
    {
      icon: '✏️',
      title: 'Naming & Identity',
      description: 'AI-generated unique brand names and visual direction'
    },
    {
      icon: '🎨',
      title: 'Design & Logo',
      description: 'Professional logo designs with brand visual guidelines'
    },
    {
      icon: '📝',
      title: 'Content Library',
      description: 'Ready-to-use marketing copy and brand messaging'
    },
    {
      icon: '📋',
      title: 'Brand Guidelines',
      description: 'Complete brand bible with usage rules'
    },
    {
      icon: '📦',
      title: 'Export Kit',
      description: 'Download all assets in multiple formats'
    },
  ];

  const examples = [
    'A smart coffee mug that tracks caffeine intake and suggests optimal drinking times',
    'An AI-powered personal stylist app for sustainable fashion',
    'A decentralized freelancer marketplace using blockchain for payments',
    'A subscription service for personalized vitamin packs based on DNA testing',
  ];

  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center px-6 py-20">
        <div className="w-full max-w-4xl space-y-12">
          {/* Hero Content */}
          <div className="text-center space-y-6 animate-fade-in">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-300 text-sm font-medium hover:bg-blue-500/20 transition-colors">
              <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              AI-Powered Brand Builder
            </div>

            <div className="space-y-4">
              <h1 className="text-5xl md:text-7xl font-black leading-tight">
                <span className="block bg-gradient-to-r from-blue-400 via-cyan-400 to-blue-600 bg-clip-text text-transparent">
                  Build Your Brand
                </span>
                <span className="block text-white mt-2">
                  in Minutes, Not Months
                </span>
              </h1>
              <p className="text-lg md:text-xl text-white/60 max-w-2xl mx-auto leading-relaxed">
                Transform your business idea into a complete, professional brand identity with AI-powered strategy, naming, design, and content—all in one platform.
              </p>
            </div>

            {/* CTA Form */}
            <div className="pt-4">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative group">
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl blur opacity-30 group-hover:opacity-50 transition duration-300" />
                  <div className="relative bg-slate-950 rounded-2xl p-4 space-y-4">
                    <label htmlFor="idea-input" className="text-xs font-semibold text-white/40 uppercase tracking-widest">
                      Your Business Idea
                    </label>
                    <textarea
                      id="idea-input"
                      value={idea}
                      onChange={(e) => setIdea(e.target.value)}
                      placeholder="Describe your business idea, product, or service..."
                      rows={4}
                      className="w-full bg-slate-900/50 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-blue-500/50 focus:ring-2 focus:ring-blue-500/20 transition-all resize-none"
                      disabled={loading}
                    />
                    {error && (
                      <p className="text-red-400 text-sm flex items-center gap-2 animate-shake">
                        <svg className="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        {error}
                      </p>
                    )}
                    <button
                      type="submit"
                      disabled={loading || !idea.trim()}
                      className="w-full px-6 py-3 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold rounded-lg transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/30 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
                    >
                      {loading ? (
                        <>
                          <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                          Creating your brand identity...
                        </>
                      ) : (
                        <>
                          <span className="text-lg">🚀</span>
                          <span>Generate Brand Identity</span>
                          <span className="opacity-0 group-hover:opacity-100 transition-opacity ml-2">→</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </form>
            </div>

            {/* Trust signals */}
            <div className="pt-8 flex flex-col sm:flex-row items-center justify-center gap-6 text-sm text-white/50">
              <div className="flex items-center gap-2">
                <span className="text-lg">⚡</span>
                <span>2-5 minutes to complete</span>
              </div>
              <div className="hidden sm:block w-px h-4 bg-white/10" />
              <div className="flex items-center gap-2">
                <span className="text-lg">💾</span>
                <span>Download all assets</span>
              </div>
              <div className="hidden sm:block w-px h-4 bg-white/10" />
              <div className="flex items-center gap-2">
                <span className="text-lg">🔄</span>
                <span>Regenerate anytime</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6 border-t border-white/5">
        <div className="max-w-6xl mx-auto space-y-12">
          <div className="text-center space-y-4">
            <h2 className="text-4xl md:text-5xl font-black text-white">
              Complete Brand <span className="text-transparent bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text">Solution</span>
            </h2>
            <p className="text-white/60 text-lg max-w-2xl mx-auto">
              Everything you need to build a professional brand identity, all powered by AI
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <FeatureCard
                key={i}
                icon={feature.icon}
                title={feature.title}
                description={feature.description}
                delay={i * 100}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Examples Section */}
      <section className="py-20 px-6 border-t border-white/5">
        <div className="max-w-4xl mx-auto space-y-8">
          <div className="text-center space-y-2">
            <h3 className="text-3xl font-black text-white">Try These Examples</h3>
            <p className="text-white/50">Click any example to get started</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {examples.map((example, i) => (
              <button
                key={i}
                onClick={() => {
                  setIdea(example);
                  document.getElementById('idea-input')?.scrollIntoView({ behavior: 'smooth' });
                  document.getElementById('idea-input')?.focus();
                }}
                className="p-4 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 text-left transition-all group"
              >
                <p className="text-white/80 group-hover:text-white transition-colors">{example}</p>
                <p className="text-xs text-white/30 mt-2">Click to use this example</p>
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
