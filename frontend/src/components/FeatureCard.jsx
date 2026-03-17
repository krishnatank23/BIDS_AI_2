export default function FeatureCard({ icon, title, description, delay = 0 }) {
  return (
    <div
      className="group relative p-6 rounded-xl bg-white/5 border border-white/10 hover:border-blue-500/50 hover:bg-white/10 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/10"
      style={{
        animation: `fadeInUp 0.6s ease-out`,
        animationDelay: `${delay}ms`,
        animationFillMode: 'both',
      }}
    >
      {/* Gradient background on hover */}
      <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-blue-500/0 to-cyan-500/0 group-hover:from-blue-500/5 group-hover:to-cyan-500/5 transition-all duration-300" />

      <div className="relative space-y-3">
        <div className="text-4xl">{icon}</div>
        <h3 className="text-lg font-bold text-white">{title}</h3>
        <p className="text-white/60 text-sm leading-relaxed">{description}</p>
      </div>

      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-12 h-12 rounded-full bg-gradient-to-br from-blue-500/10 to-cyan-500/10 -mr-6 -mt-6 group-hover:scale-150 transition-transform duration-300 opacity-0 group-hover:opacity-100" />
    </div>
  );
}
