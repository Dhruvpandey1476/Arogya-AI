const CONFIG = {
  Low:       { className: 'severity-low',       dot: 'bg-emerald-400' },
  Medium:    { className: 'severity-medium',     dot: 'bg-yellow-400' },
  High:      { className: 'severity-high',       dot: 'bg-orange-400' },
  Emergency: { className: 'severity-emergency',  dot: 'bg-red-400' },
}

export default function SeverityBadge({ severity, large = false }) {
  const cfg = CONFIG[severity] || CONFIG.Low
  return (
    <span className={`inline-flex items-center gap-2 rounded-full font-semibold
                      ${large ? 'px-4 py-2 text-sm' : 'px-3 py-1 text-xs'}
                      ${cfg.className}`}>
      <span className={`w-2 h-2 rounded-full ${cfg.dot} ${severity === 'Emergency' ? 'animate-pulse' : ''}`} />
      {severity}
    </span>
  )
}
