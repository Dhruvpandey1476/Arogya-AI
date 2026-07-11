import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sliders, RotateCcw } from 'lucide-react'
import InputTabs from '../components/assessment/InputTabs'
import ResultCard from '../components/assessment/ResultCard'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import useAssessmentStore from '../store/assessmentStore'
import { assessmentService } from '../services/api'

export default function AssessmentPage() {
  const [showResult, setShowResult] = useState(false)
  const store = useAssessmentStore()

  const handleSubmit = async () => {
    if (store.selectedSymptoms.length === 0 && !store.symptomText && !store.imageBase64) {
      alert('Please select at least one symptom, record voice, or upload a skin image.')
      return
    }

    store.setLoading(true)
    setShowResult(false)

    try {
      const payload = {
        symptoms: store.selectedSymptoms,
        symptom_text: store.symptomText || null,
        duration_days: store.durationDays,
        pain_scale: store.painScale,
        fever: store.fever,
        fever_temp: store.feverTemp ? parseFloat(store.feverTemp) : null,
        age: store.age,
        image_base64: store.imageBase64 || null,
      }

      const result = await assessmentService.submit(payload)
      store.setResult(result)
      setShowResult(true)
    } catch (err) {
      store.setError(err?.response?.data?.detail || err.message || 'Assessment failed. Is the backend running?')
    } finally {
      store.setLoading(false)
    }
  }

  const handleReset = () => {
    store.reset()
    setShowResult(false)
  }

  return (
    <div className="pt-24 pb-16 px-6 min-h-screen">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="mb-8">
          <p className="text-xs text-slate-500 uppercase tracking-widest font-mono mb-2">Health Triage</p>
          <h1 className="font-display text-4xl font-bold text-slate-100">
            Symptom <span className="text-emerald-400">Assessment</span>
          </h1>
          <p className="text-slate-400 mt-2 text-sm">
            Select symptoms, record voice, or upload a skin image. All three inputs can be combined.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left panel — Inputs */}
          <div className="space-y-6">
            {/* Main input tabs */}
            <div className="glass-strong rounded-2xl p-6">
              <InputTabs />
            </div>

            {/* Patient details */}
            <div className="glass-strong rounded-2xl p-6">
              <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
                <Sliders size={14} className="text-emerald-400" />
                Patient Details
              </h3>

              <div className="grid grid-cols-2 gap-4">
                {/* Age */}
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Age</label>
                  <input
                    type="number"
                    min={0} max={120}
                    value={store.age}
                    onChange={(e) => store.setAge(parseInt(e.target.value) || 0)}
                    className="input-field"
                  />
                </div>

                {/* Duration */}
                <div>
                  <label className="text-xs text-slate-500 mb-1.5 block">Duration (days)</label>
                  <input
                    type="number"
                    min={1} max={365}
                    value={store.durationDays}
                    onChange={(e) => store.setDurationDays(parseInt(e.target.value) || 1)}
                    className="input-field"
                  />
                </div>

                {/* Pain scale */}
                <div className="col-span-2">
                  <label className="text-xs text-slate-500 mb-1.5 flex justify-between">
                    <span>Pain Scale</span>
                    <span className="text-emerald-400 font-mono">{store.painScale}/10</span>
                  </label>
                  <input
                    type="range"
                    min={0} max={10}
                    value={store.painScale}
                    onChange={(e) => store.setPainScale(parseInt(e.target.value))}
                    className="w-full accent-emerald-500"
                  />
                  <div className="flex justify-between text-xs text-slate-600 mt-1">
                    <span>No pain</span><span>Severe</span>
                  </div>
                </div>

                {/* Fever toggle */}
                <div className="col-span-2 flex items-center justify-between glass rounded-xl px-4 py-3">
                  <span className="text-sm text-slate-300">Fever present?</span>
                  <button
                    onClick={() => store.setFever(!store.fever)}
                    className={`relative w-11 h-6 rounded-full transition-colors duration-200
                                ${store.fever ? 'bg-emerald-500' : 'bg-slate-700'}`}
                  >
                    <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform duration-200
                                      ${store.fever ? 'translate-x-6' : 'translate-x-1'}`} />
                  </button>
                </div>

                {/* Fever temp (conditional) */}
                {store.fever && (
                  <div className="col-span-2">
                    <label className="text-xs text-slate-500 mb-1.5 block">Temperature (°C)</label>
                    <input
                      type="number"
                      step="0.1" min={36} max={42}
                      placeholder="e.g. 38.5"
                      value={store.feverTemp}
                      onChange={(e) => store.setFeverTemp(e.target.value)}
                      className="input-field"
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Submit */}
            <div className="flex gap-3">
              <button
                onClick={handleSubmit}
                disabled={store.isLoading}
                className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {store.isLoading ? 'Analyzing...' : 'Run Assessment'}
              </button>
              {showResult && (
                <button onClick={handleReset} className="btn-secondary flex items-center gap-2 px-4">
                  <RotateCcw size={15} />
                </button>
              )}
            </div>

            {store.error && (
              <div className="bg-red-500/10 border border-red-500/25 rounded-xl p-4 text-red-400 text-sm">
                {store.error}
              </div>
            )}
          </div>

          {/* Right panel — Results */}
          <div className="lg:sticky lg:top-24 lg:self-start">
            <AnimatePresence mode="wait">
              {store.isLoading && (
                <motion.div key="loading"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  className="glass-strong rounded-2xl p-6"
                >
                  <LoadingSpinner />
                </motion.div>
              )}
              {!store.isLoading && showResult && (
                <motion.div key="result"
                  initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  className="glass-strong rounded-2xl p-6"
                >
                  <ResultCard />
                </motion.div>
              )}
              {!store.isLoading && !showResult && (
                <motion.div key="empty"
                  initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                  className="glass rounded-2xl p-12 flex flex-col items-center justify-center text-center gap-4"
                >
                  <div className="w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/15
                                  flex items-center justify-center animate-float">
                    <span className="text-3xl">🩺</span>
                  </div>
                  <div>
                    <p className="text-slate-300 font-medium">Results will appear here</p>
                    <p className="text-slate-600 text-sm mt-1">Fill in symptoms and click Run Assessment</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  )
}
