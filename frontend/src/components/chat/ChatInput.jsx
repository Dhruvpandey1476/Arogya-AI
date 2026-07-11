import { useState } from 'react'
import { Send } from 'lucide-react'

export default function ChatInput({ onSend, disabled }) {
  const [value, setValue] = useState('')

  const handleSend = () => {
    const msg = value.trim()
    if (!msg || disabled) return
    onSend(msg)
    setValue('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex gap-3 items-end">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about your condition, symptoms, medications, first aid..."
        disabled={disabled}
        rows={1}
        className="input-field flex-1 resize-none disabled:opacity-50 min-h-[44px] max-h-32
                   overflow-y-auto leading-relaxed py-3"
        style={{ fieldSizing: 'content' }}
      />
      <button
        onClick={handleSend}
        disabled={disabled || !value.trim()}
        className="w-11 h-11 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950
                   flex items-center justify-center transition-all duration-200
                   disabled:opacity-40 disabled:cursor-not-allowed active:scale-95 shrink-0"
      >
        <Send size={16} />
      </button>
    </div>
  )
}
