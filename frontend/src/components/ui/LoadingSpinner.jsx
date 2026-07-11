import { Loader2 } from 'lucide-react'

export default function LoadingSpinner({ message = 'Analyzing...' }) {
  return (
    <div className="flex flex-col items-center gap-4 py-12">
      <div className="relative">
        <div className="w-16 h-16 rounded-full border-2 border-emerald-500/20 flex items-center justify-center">
          <Loader2 size={28} className="text-emerald-400 animate-spin" />
        </div>
        <div className="absolute inset-0 rounded-full border-t-2 border-emerald-400 animate-spin" />
      </div>
      <div className="text-center">
        <p className="text-slate-300 font-medium">{message}</p>
        <p className="text-slate-600 text-sm mt-1">Running ML models and RAG retrieval...</p>
      </div>
    </div>
  )
}
