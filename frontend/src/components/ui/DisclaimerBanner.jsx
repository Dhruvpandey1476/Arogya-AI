import { ShieldAlert } from 'lucide-react'

export default function DisclaimerBanner({ text }) {
  return (
    <div className="flex items-start gap-3 bg-yellow-500/5 border border-yellow-500/20 rounded-xl p-4">
      <ShieldAlert size={16} className="text-yellow-400 mt-0.5 shrink-0" />
      <p className="text-yellow-200/70 text-xs leading-relaxed">
        {text || 'Arogya AI is not a substitute for professional medical advice. Always consult a qualified healthcare provider.'}
      </p>
    </div>
  )
}
