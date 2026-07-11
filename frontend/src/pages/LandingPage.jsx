import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Activity, Mic, Image, Brain, ShieldCheck, Zap, ArrowRight } from 'lucide-react'

const features = [
  { icon: Brain, title: 'ML Disease Prediction', desc: 'Ensemble of Random Forest, XGBoost & SVM trained on 41 diseases and 132 symptoms' },
  { icon: Image, title: 'Skin CV Classifier', desc: 'EfficientNet-B0 fine-tuned on ISIC dataset for skin condition detection' },
  { icon: Mic, title: 'Voice Input', desc: 'Speak your symptoms in Hindi or English — Whisper transcribes and translates' },
  { icon: Activity, title: 'RAG-Grounded LLM', desc: 'Phi-3 Mini explains predictions using retrieved WHO & MedlinePlus documents' },
  { icon: ShieldCheck, title: 'Severity Triage', desc: 'XGBoost classifier assigns Low / Medium / High / Emergency urgency level' },
  { icon: Zap, title: 'Health Chatbot', desc: 'Conversational follow-up grounded in your assessment context' },
]

const fade = { hidden: { opacity: 0, y: 24 }, show: { opacity: 1, y: 0 } }

export default function LandingPage() {
  return (
    <div className="pt-24 pb-16 px-6">
      <div className="max-w-5xl mx-auto">

        {/* Hero */}
        <motion.div
          className="text-center mb-20"
          initial="hidden" animate="show"
          variants={{ show: { transition: { staggerChildren: 0.12 } } }}
        >
          <motion.div variants={fade}
            className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full text-emerald-400 text-sm font-medium mb-8"
          >
            <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse-slow" />
            Multimodal Health Triage System
          </motion.div>

          <motion.h1 variants={fade}
            className="font-display text-5xl sm:text-7xl font-bold text-slate-100 mb-6 leading-tight"
          >
            आरोग्य <span className="text-emerald-400 glow-text">AI</span>
          </motion.h1>

          <motion.p variants={fade}
            className="text-slate-400 text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed"
          >
            Not just another chatbot. A three-layer AI system that predicts with ML,
            sees with deep learning, and explains with RAG-grounded language models.
          </motion.p>

          <motion.div variants={fade} className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/assess" className="btn-primary flex items-center justify-center gap-2 text-base">
              Start Assessment <ArrowRight size={18} />
            </Link>
            <Link to="/chat" className="btn-secondary flex items-center justify-center gap-2 text-base">
              Chat with Arogya
            </Link>
          </motion.div>
        </motion.div>

        {/* Architecture Diagram */}
        <motion.div
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}
          className="glass rounded-2xl p-6 mb-20 glow-emerald"
        >
          <p className="text-center text-xs text-slate-500 uppercase tracking-widest mb-6 font-mono">System Architecture</p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 text-sm flex-wrap">
            {['Symptom Input', 'Voice / Text / Image', 'ML Prediction', 'CV Classifier', 'RAG Retrieval', 'LLM Explanation', 'Triage Card'].map((step, i, arr) => (
              <div key={step} className="flex items-center gap-3">
                <div className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium
                  ${i === 0 ? 'bg-slate-700/60 text-slate-300' :
                    i === arr.length - 1 ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' :
                    'bg-emerald-900/30 text-emerald-400/80'}`}>
                  {step}
                </div>
                {i < arr.length - 1 && <span className="text-emerald-700 text-lg">→</span>}
              </div>
            ))}
          </div>
        </motion.div>

        {/* Features grid */}
        <motion.div
          className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5"
          initial="hidden" animate="show"
          variants={{ show: { transition: { staggerChildren: 0.08, delayChildren: 0.4 } } }}
        >
          {features.map(({ icon: Icon, title, desc }) => (
            <motion.div key={title} variants={fade}
              className="glass rounded-2xl p-6 hover:border-emerald-500/25 transition-all duration-300 group"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20
                              flex items-center justify-center mb-4 group-hover:bg-emerald-500/20 transition-colors">
                <Icon size={18} className="text-emerald-400" />
              </div>
              <h3 className="font-display font-semibold text-slate-100 mb-2">{title}</h3>
              <p className="text-slate-400 text-sm leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Disclaimer */}
        <div className="mt-16 text-center">
          <p className="text-slate-600 text-xs max-w-lg mx-auto leading-relaxed">
            Arogya AI is a health awareness and triage tool, not a medical diagnostic device.
            Always consult a qualified healthcare professional for medical advice, diagnosis, and treatment.
          </p>
        </div>
      </div>
    </div>
  )
}
