import { Activity } from 'lucide-react'

export default function MessageBubble({ role, content, isStreaming = false }) {
  const isUser = role === 'user'

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center
                        ${isUser
                          ? 'bg-slate-700 border border-slate-600 text-slate-300 text-xs font-semibold'
                          : 'bg-emerald-500/20 border border-emerald-500/30'}`}>
        {isUser ? 'U' : <Activity size={14} className="text-emerald-400" />}
      </div>

      {/* Bubble */}
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed
                        ${isUser
                          ? 'bg-slate-700/80 text-slate-200 rounded-tr-sm border border-slate-600/50'
                          : 'glass text-slate-300 rounded-tl-sm'}`}>
        {content}
        {isStreaming && (
          <span className="inline-flex gap-1 ml-1.5 align-middle">
            {[0, 1, 2].map((i) => (
              <span key={i} className="typing-dot w-1.5 h-1.5 bg-emerald-400 rounded-full inline-block"
                    style={{ animationDelay: `${i * 0.2}s` }} />
            ))}
          </span>
        )}
      </div>
    </div>
  )
}
