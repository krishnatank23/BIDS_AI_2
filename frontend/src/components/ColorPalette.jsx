/**
 * ColorPalette – Renders a visual representation of the brand's color palette.
 */
export default function ColorPalette({ palette }) {
  if (!palette) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mt-4">
      {Object.entries(palette).map(([key, data]) => (
        <div key={key} className="glass-card p-3 flex flex-col items-center space-y-3 group transition-all duration-300 hover:scale-[1.02]">
          <div 
            className="w-full h-24 rounded-xl shadow-inner border border-white/10"
            style={{ backgroundColor: data.hex }}
          >
            {/* Hover copy hex code */}
            <div className="w-full h-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/20 rounded-xl cursor-pointer"
                 onClick={() => navigator.clipboard.writeText(data.hex)}>
              <span className="text-xs font-bold text-white drop-shadow-md">Copy Hex</span>
            </div>
          </div>
          <div className="text-center">
            <h5 className="text-sm font-bold text-white uppercase tracking-tight">{data.name}</h5>
            <p className="text-[10px] text-brand-300 font-mono mt-1 opacity-80">{data.hex}</p>
            <p className="text-[10px] text-white/40 mt-2 leading-tight italic">{data.usage}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
