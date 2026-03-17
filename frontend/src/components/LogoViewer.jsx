/**
 * LogoViewer – displays 2-3 logo variations with selection and regeneration
 */
import { useState } from 'react';
import RegenerateButton from './RegenerateButton';

export default function LogoViewer({ logoData, onRegenerate }) {
  if (!logoData) return null;

  const { logos, total_variations } = logoData;
  const [selectedIndex, setSelectedIndex] = useState(0);

  if (!logos || logos.length === 0) return null;

  const selected = logos[selectedIndex];
  const isSvg = selected.format === 'svg';
  const imgSrc = isSvg
    ? `data:image/svg+xml;base64,${selected.logo_base64}`
    : `data:image/png;base64,${selected.logo_base64}`;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Main Logo Display */}
      <div className="glass-card p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-black text-white uppercase tracking-tight">Logo Variations</h3>
          <span className="text-sm font-bold text-white/50">
            {selectedIndex + 1} of {total_variations}
          </span>
        </div>

        {/* Selected Logo */}
        <div className="flex justify-center">
          <div className="relative group">
            <div className="absolute -inset-6 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-3xl blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <img
              src={imgSrc}
              alt={`Logo variation: ${selected.variant_name}`}
              className="relative w-80 h-80 object-contain rounded-2xl bg-white/95 p-6 shadow-2xl shadow-blue-500/20"
            />
          </div>
        </div>

        {/* Variation Name */}
        <div className="text-center">
          <h4 className="text-lg font-bold text-white mb-1">{selected.variant_name}</h4>
          <p className="text-xs text-white/40">Style: {selected.variant_name}</p>
        </div>

        {/* Thumbnail Navigation */}
        <div className="flex gap-4 justify-center mt-8">
          {logos.map((logo, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedIndex(idx)}
              className={`group relative w-20 h-20 rounded-lg overflow-hidden transition-all ${
                idx === selectedIndex
                  ? 'ring-2 ring-cyan-400 shadow-lg shadow-cyan-500/30'
                  : 'ring-1 ring-white/10 hover:ring-white/30'
              }`}
            >
              <img
                src={
                  logo.format === 'svg'
                    ? `data:image/svg+xml;base64,${logo.logo_base64}`
                    : `data:image/png;base64,${logo.logo_base64}`
                }
                alt={`${logo.variant_name} thumbnail`}
                className="w-full h-full object-contain bg-white/90 p-2"
              />
              <div className="absolute inset-0 bg-white/0 group-hover:bg-white/10 transition-colors" />
              <div className="absolute bottom-1 left-1 right-1 text-[9px] font-bold text-white/70 text-center truncate">
                {logo.variant_name.split(' ')[0]}
              </div>
            </button>
          ))}
        </div>

        {/* Debug Info */}
        <details className="text-left">
          <summary className="text-xs text-white/30 cursor-pointer hover:text-white/50 transition-colors">
            Logo Details
          </summary>
          <div className="mt-3 space-y-1 text-xs text-white/40 bg-white/5 rounded-lg p-3">
            <p>Method: <span className="text-white/60">{selected.generation_method}</span></p>
            <p>Format: <span className="text-white/60">{selected.format?.toUpperCase()}</span></p>
            {selected.generation_prompt && (
              <p className="mt-2 text-white/50">
                Prompt: <span className="text-white/40 text-[10px]">{selected.generation_prompt.substring(0, 100)}...</span>
              </p>
            )}
          </div>
        </details>

        {/* Regenerate Individual Variation */}
        {onRegenerate && (
          <div className="flex gap-3 pt-4 border-t border-white/10">
            <button
              onClick={() => onRegenerate('logo_generator', `regenerate only ${selected.variant_name} style`)}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/30 text-blue-300 hover:text-blue-200 font-semibold transition-all text-sm"
            >
              <span>🔄</span>
              <span>Regenerate This Variation</span>
            </button>
            <button
              onClick={() => onRegenerate('logo_generator', 'regenerate all logo variations with fresh ideas')}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-cyan-600/20 hover:bg-cyan-600/30 border border-cyan-500/30 text-cyan-300 hover:text-cyan-200 font-semibold transition-all text-sm"
            >
              <span>✨</span>
              <span>Regenerate All</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
