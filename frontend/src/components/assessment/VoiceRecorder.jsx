import { useState, useRef } from 'react'
import { Mic, MicOff, Loader2 } from 'lucide-react'
import { voiceService } from '../../services/api'
import useAssessmentStore from '../../store/assessmentStore'

export default function VoiceRecorder() {
  const [recording, setRecording] = useState(false)
  const [loading, setLoading] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [lang, setLang] = useState('')
  const mediaRef = useRef(null)
  const chunksRef = useRef([])
  const { setSymptomText } = useAssessmentStore()

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mr = new MediaRecorder(stream)
      mediaRef.current = mr
      chunksRef.current = []
      mr.ondataavailable = (e) => chunksRef.current.push(e.data)
      mr.onstop = handleStop
      mr.start()
      setRecording(true)
    } catch (err) {
      alert('Microphone access denied. Please allow microphone permissions.')
    }
  }

  const stopRecording = () => {
    mediaRef.current?.stop()
    mediaRef.current?.stream.getTracks().forEach((t) => t.stop())
    setRecording(false)
  }

  const handleStop = async () => {
    setLoading(true)
    try {
      const blob = new Blob(chunksRef.current, { type: 'audio/wav' })
      const result = await voiceService.transcribe(blob)
      setTranscript(result.transcript)
      setLang(result.detected_language)
      setSymptomText(result.transcript_english || result.transcript)
    } catch (err) {
      setTranscript('Transcription failed. Please type your symptoms manually.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col items-center gap-6 py-4">
      {/* Mic button */}
      <button
        onClick={recording ? stopRecording : startRecording}
        disabled={loading}
        className={`relative w-20 h-20 rounded-full flex items-center justify-center
          transition-all duration-300
          ${recording
            ? 'bg-red-500/20 border-2 border-red-500 text-red-400 shadow-lg shadow-red-500/20'
            : 'bg-emerald-500/15 border-2 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/25'
          } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        {loading ? (
          <Loader2 size={28} className="animate-spin" />
        ) : recording ? (
          <>
            <MicOff size={28} />
            <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
          </>
        ) : (
          <Mic size={28} />
        )}
      </button>

      {/* Waveform animation while recording */}
      {recording && (
        <div className="flex items-end gap-1 h-8">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="wave-bar" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
      )}

      <p className="text-slate-400 text-sm text-center">
        {loading ? 'Transcribing...' :
         recording ? 'Recording... Tap to stop' :
         'Tap to start recording'}
      </p>

      {transcript && (
        <div className="w-full glass rounded-xl p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-slate-500 uppercase tracking-wide font-mono">Transcript</span>
            {lang && lang !== 'en' && (
              <span className="text-xs bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-500/20">
                Detected: {lang} → EN
              </span>
            )}
          </div>
          <p className="text-slate-300 text-sm leading-relaxed">{transcript}</p>
        </div>
      )}

      <p className="text-xs text-slate-600 text-center max-w-xs">
        Supports Hindi, English, and other Indian languages.
        Transcription powered by OpenAI Whisper.
      </p>
    </div>
  )
}
