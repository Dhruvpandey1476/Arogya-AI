export default function ConfidenceBar({ value, label, rank = 0 }) {
  const colors = ['bg-emerald-400', 'bg-emerald-500/70', 'bg-emerald-600/50']
  const color = colors[rank] || colors[2]

  return (
    <div className="w-full">
      <div className="flex justify-between items-center mb-1.5">
        <span className="text-slate-200 text-sm font-medium truncate pr-4">{label}</span>
        <span className="text-slateald-400 text-sm font-mono shrink-0">{value.toFixed(1)}%</span>
      </div>
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color} transition-all duration-700 ease-out`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  )
}
