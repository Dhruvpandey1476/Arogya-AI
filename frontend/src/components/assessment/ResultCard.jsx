import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { MessageCircle, Stethoscope, BookOpen, CheckCircle, Eye } from 'lucide-react'
import SeverityBadge from '../ui/SeverityBadge'
import ConfidenceBar from '../ui/ConfidenceBar'
import DisclaimerBanner from '../ui/DisclaimerBanner'
import useAssessmentStore from '../../store/assessmentStore'

const RISK_COLORS = {
  benign:      'text-emerald-400 bg-emerald-500/10 border-emerald-500/25',
  monitor:     'text-yellow-400 bg-yellow-500/10 border-yellow-500/25',
  concerning:  'text-red-400 bg-red-500/10 border-red-500/25',
}

export default function ResultCard() {
  const navigate = useNavigate()
  const {
    sessionId, diseases, severity, cvResult,
    explanation, firstAidSteps, specialist,
    sources, disclaimer,
  } = useAssessmentStore()

  const fade = { hidden: { opacity: 0, y: 16 }, show: { opacity: 1, y: 0 } }

  return (
    <motion.div
      initial="hidden" animate="show"
      variants={{ show: { transition: { staggerChildren: 0.1 } } }}
      className="space-y-5"
    >
      {/* Header row */}
      <motion.div variants={fade} className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs text-slate-500 uppercase tracking-widest font-mono mb-1">Assessment Complete</p>
          <h2 className="font-display text-2xl font-bold text-slate-100">Your Triage Report</h2>
        </div>
        <SeverityBadge severity={severity} large />
      </motion.div>

      {/* Disease predictions */}
      {diseases.length > 0 && (
        <motion.div variants={fade} className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4 flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            ML Prediction — Top {diseases.length} Conditions
          </h3>
          <div className="space-y-4">
            {diseases.map((d, i) => (
              <div key={d.name}>
                <ConfidenceBar label={d.name} value={d.confidence} rank={i} />
                {d.description && (
                  <p className="text-slate-500 text-xs mt-1 ml-0.5 leading-relaxed">{d.description}</p>
                )}
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* CV result */}
      {cvResult && (
        <motion.div variants={fade} className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Eye size={14} className="text-emerald-400" />
            Skin Image Analysis — EfficientNet-B0
          </h3>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-slate-100 font-medium">{cvResult.condition}</p>
              <p className="text-slate-500 text-xs mt-0.5">{cvResult.confidence.toFixed(1)}% confidence</p>
            </div>
            <span className={`px-3 py-1.5 rounded-lg text-xs font-semibold border capitalize
                              ${RISK_COLORS[cvResult.risk_level] || RISK_COLORS.monitor}`}>
              {cvResult.risk_level}
            </span>
          </div>
        </motion.div>
      )}

      {/* LLM Explanation */}
      {explanation && (
        <motion.div variants={fade} className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            AI Explanation <span className="text-slate-600 font-normal">(RAG-grounded)</span>
          </h3>
          <p className="text-slate-300 text-sm leading-relaxed">{explanation}</p>
          {sources.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {sources.map((s) => (
                <span key={s} className="flex items-center gap-1.5 text-xs text-slate-500 bg-slate-800/60 px-2.5 py-1 rounded-full border border-slate-700/50">
                  <BookOpen size={10} />
                  {s}
                </span>
              ))}
            </div>
          )}
        </motion.div>
      )}

      {/* Specialist + First Aid */}
      <motion.div variants={fade} className="grid sm:grid-cols-2 gap-5">
        {/* Specialist */}
        <div className="glass rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
            <Stethoscope size={14} className="text-emerald-400" />
            Recommended Specialist
          </h3>
          <p className="text-emerald-300 font-semibold text-lg font-display">{specialist || 'General Physician'}</p>
          <p className="text-slate-500 text-xs mt-1">Consult for accurate diagnosis and treatment</p>
        </div>

        {/* First aid steps */}
        {firstAidSteps.length > 0 && (
          <div className="glass rounded-2xl p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-3 flex items-center gap-2">
              <CheckCircle size={14} className="text-emerald-400" />
              Immediate Steps
            </h3>
            <ul className="space-y-2">
              {firstAidSteps.map((step, i) => (
                <li key={i} className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-500/15 border border-emerald-500/30
                                   text-emerald-400 text-xs flex items-center justify-center shrink-0 font-mono mt-0.5">
                    {i + 1}
                  </span>
                  <span className="text-slate-400 text-xs leading-relaxed">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </motion.div>

      {/* Disclaimer */}
      <motion.div variants={fade}>
        <DisclaimerBanner text={disclaimer} />
      </motion.div>

      {/* Chat CTA */}
      {sessionId && (
        <motion.div variants={fade}>
          <button
            onClick={() => navigate(`/chat/${sessionId}`)}
            className="btn-primary w-full flex items-center justify-center gap-2"
          >
            <MessageCircle size={18} />
            Discuss this with Arogya AI
          </button>
        </motion.div>
      )}
    </motion.div>
  )
}
