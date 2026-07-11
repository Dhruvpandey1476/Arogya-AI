import { useState } from 'react'
import { Search, X } from 'lucide-react'
import useAssessmentStore from '../../store/assessmentStore'
import { SYMPTOM_CATEGORIES, formatSymptom } from '../../utils/symptomList'

export default function SymptomSelector() {
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState('General')
  const { selectedSymptoms, toggleSymptom, removeSymptom } = useAssessmentStore()

  const filtered = search.trim()
    ? Object.values(SYMPTOM_CATEGORIES)
        .flat()
        .filter((s) => s.includes(search.toLowerCase().replace(/ /g, '_')))
    : SYMPTOM_CATEGORIES[activeCategory] || []

  return (
    <div>
      {/* Selected symptoms chips */}
      {selectedSymptoms.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {selectedSymptoms.map((s) => (
            <span key={s}
              className="flex items-center gap-1.5 bg-emerald-500/15 border border-emerald-500/30
                         text-emerald-300 text-xs px-3 py-1.5 rounded-full font-medium"
            >
              {formatSymptom(s)}
              <button onClick={() => removeSymptom(s)} className="hover:text-red-400 transition-colors">
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Search */}
      <div className="relative mb-4">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search symptoms..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-field pl-9"
        />
      </div>

      {/* Category tabs */}
      {!search && (
        <div className="flex gap-2 flex-wrap mb-4">
          {Object.keys(SYMPTOM_CATEGORIES).map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all duration-200
                ${activeCategory === cat
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                  : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'}`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* Symptom grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 max-h-56 overflow-y-auto pr-1">
        {filtered.map((s) => {
          const selected = selectedSymptoms.includes(s)
          return (
            <button
              key={s}
              onClick={() => toggleSymptom(s)}
              className={`px-3 py-2 rounded-lg text-left text-xs font-medium transition-all duration-150
                ${selected
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : 'glass text-slate-400 hover:text-slate-200 hover:border-slate-600/60'}`}
            >
              {formatSymptom(s)}
            </button>
          )
        })}
        {filtered.length === 0 && (
          <p className="col-span-3 text-slate-600 text-xs text-center py-4">No symptoms found</p>
        )}
      </div>

      <p className="text-slate-600 text-xs mt-3">
        {selectedSymptoms.length} symptom{selectedSymptoms.length !== 1 ? 's' : ''} selected
      </p>
    </div>
  )
}
