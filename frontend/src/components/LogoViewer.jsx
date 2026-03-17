/**
 * LogoViewer – displays the generated logo (base64 or SVG).
 */
export default function LogoViewer({ logoData }) {
  if (!logoData) return null;

  const { logo_base64, generation_method, format, generation_prompt } = logoData;

  const isSvg = format === 'svg';
  const imgSrc = isSvg
    ? `data:image/svg+xml;base64,${logo_base64}`
    : `data:image/png;base64,${logo_base64}`;

  return (
    <div className="glass-card p-6 text-center space-y-4" id="logo-viewer">
      <h3 className="text-lg font-semibold gradient-text">Generated Logo</h3>

      <div className="flex justify-center">
        <div className="relative group">
          <div className="absolute -inset-4 bg-gradient-to-r from-brand-500/20 to-brand-400/20 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
          <img
            src={imgSrc}
            alt="Generated brand logo"
            className="relative w-64 h-64 object-contain rounded-xl bg-white/90 p-4 shadow-2xl shadow-brand-500/10"
          />
        </div>
      </div>

      <div className="text-white/40 text-xs space-y-1">
        <p>Method: <span className="text-white/60">{generation_method}</span></p>
        <p>Format: <span className="text-white/60">{format?.toUpperCase()}</span></p>
      </div>

      {generation_prompt && (
        <details className="text-left">
          <summary className="text-xs text-white/30 cursor-pointer hover:text-white/50 transition-colors">
            View generation prompt
          </summary>
          <p className="mt-2 text-xs text-white/40 bg-white/5 rounded-lg p-3">
            {generation_prompt}
          </p>
        </details>
      )}
    </div>
  );
}
