import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Stethoscope } from 'lucide-react'
import ChatWindow from '../components/chat/ChatWindow'
import useAssessmentStore from '../store/assessmentStore'

export default function ChatPage() {
  const { sessionId: paramSessionId } = useParams()
  const { sessionId: storeSessionId, diseases, severity } = useAssessmentStore()
  const sessionId = paramSessionId || storeSessionId

  return (
    <div className="pt-20 pb-6 px-6 min-h-screen">
      <div className="max-w-3xl mx-auto h-[calc(100vh-6rem)] flex flex-col">

        {/* Header */}
        <div className="flex items-center justify-between mb-6 shrink-0">
          <div className="flex items-center gap-4">
            <Link to="/assess"
              className="w-9 h-9 glass rounded-xl flex items-center justify-center
                         text-slate-400 hover:text-slate-200 transition-colors">
              <ArrowLeft size={16} />
            </Link>
            <div>
              <h1 className="font-display text-2xl font-bold text-slate-100">
                Chat with <span className="text-emerald-400">Arogya</span>
              </h1>
              {diseases.length > 0 && (
                <p className="text-slate-500 text-xs mt-0.5">
                  Context: {diseases[0]?.name} · Severity: {severity}
                </p>
              )}
            </div>
          </div>

          {!sessionId && (
            <Link to="/assess" className="btn-primary flex items-center gap-2 text-sm py-2">
              <Stethoscope size={14} />
              Start Assessment
            </Link>
          )}
        </div>

        {/* Chat window */}
        <div className="flex-1 glass-strong rounded-2xl p-6 overflow-hidden flex flex-col min-h-0">
          <ChatWindow sessionId={sessionId} />
        </div>

        {/* Footer note */}
        <p className="text-center text-slate-700 text-xs mt-4 shrink-0">
          Arogya AI provides health information, not medical diagnosis. Always consult a doctor.
        </p>
      </div>
    </div>
  )
}
