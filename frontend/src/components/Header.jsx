export default function Header({ projectActive }) {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-sm border-b border-white/5 bg-slate-950/50">
      <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
            <span className="text-white font-bold text-lg">✨</span>
          </div>
          <div className="hidden sm:block">
            <h1 className="text-lg font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              BrandAI
            </h1>
            <p className="text-xs text-white/40">AI-Powered Brand Builder</p>
          </div>
        </div>

        {/* Nav items */}
        <div className="flex items-center gap-6">
          <nav className="hidden md:flex items-center gap-8 text-sm">
            <a href="#" className="text-white/60 hover:text-white transition-colors">Features</a>
            <a href="#" className="text-white/60 hover:text-white transition-colors">Docs</a>
            <a href="#" className="text-white/60 hover:text-white transition-colors">Pricing</a>
          </nav>

          {/* Status indicator */}
          {projectActive && (
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-xs text-emerald-300 font-medium">Project Active</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
