import { useState } from 'react'
import { Type, Mic, Image } from 'lucide-react'
import SymptomSelector from './SymptomSelector'
import VoiceRecorder from './VoiceRecorder'
import ImageUploader from './ImageUploader'

const TABS = [
  { id: 'text', label: 'Symptoms', icon: Type },
  { id: 'voice', label: 'Voice', icon: Mic },
  { id: 'image', label: 'Skin Image', icon: Image },
]

export default function InputTabs() {
  const [active, setActive] = useState('text')

  return (
    <div>
      {/* Tab bar */}
      <div className="flex gap-1 glass rounded-xl p-1 mb-6">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActive(id)}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg
                        text-sm font-medium transition-all duration-200
                        ${active === id
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : 'text-slate-500 hover:text-slate-300'}`}
          >
            <Icon size={15} />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="min-h-64">
        {active === 'text' && <SymptomSelector />}
        {active === 'voice' && <VoiceRecorder />}
        {active === 'image' && <ImageUploader />}
      </div>
    </div>
  )
}
