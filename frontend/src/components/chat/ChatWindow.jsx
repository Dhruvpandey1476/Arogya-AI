import { useEffect, useRef, useState } from 'react'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import { API_BASE_URL } from '../../services/api'

// Convert http(s):// base to ws(s):// for the chat WebSocket
const WS_BASE_URL = API_BASE_URL.replace(/^http/, 'ws')

const SUGGESTED = [
  'What foods should I avoid?',
  'Is this contagious?',
  'When should I go to hospital?',
  'What causes this condition?',
  'Can children get this too?',
]

export default function ChatWindow({ sessionId }) {
  const [messages, setMessages] = useState([])
  const [streaming, setStreaming] = useState(false)
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)
  const bottomRef = useRef(null)
  const streamBufferRef = useRef('')

  useEffect(() => {
    if (!sessionId) return

    const url = `${WS_BASE_URL}/ws/chat/${sessionId}`
    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      setError(null)
      setMessages([{
        role: 'assistant',
        content: "Hello! I'm Arogya AI. I have your assessment results. Ask me anything about your symptoms, the predicted conditions, first aid steps, or general health questions.",
      }])
    }

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data)

      if (data.type === 'start') {
        streamBufferRef.current = ''
        setStreaming(true)
        setMessages((prev) => [...prev, { role: 'assistant', content: '', isStreaming: true }])
      } else if (data.type === 'token') {
        streamBufferRef.current += data.content
        const buf = streamBufferRef.current
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1] = { role: 'assistant', content: buf, isStreaming: true }
          return updated
        })
      } else if (data.type === 'end') {
        const final = streamBufferRef.current
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1] = { role: 'assistant', content: final, isStreaming: false }
          return updated
        })
        setStreaming(false)
      } else if (data.type === 'error') {
        setError(data.content)
        setStreaming(false)
      } else if (data.type === 'message') {
        setMessages((prev) => [...prev, { role: 'assistant', content: data.content }])
      }
    }

    ws.onerror = () => setError('WebSocket connection failed. Is the backend running?')
    ws.onclose = () => setConnected(false)

    return () => ws.close()
  }, [sessionId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = (text) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError('Connection lost. Please refresh.')
      return
    }
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    wsRef.current.send(JSON.stringify({ message: text }))
  }

  return (
    <div className="flex flex-col h-full">
      {/* Connection status */}
      <div className="flex items-center gap-2 mb-4">
        <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-slate-600'}`} />
        <span className="text-xs text-slate-500 font-mono">
          {connected ? 'Connected' : 'Disconnected'}
        </span>
        {sessionId && (
          <span className="ml-auto text-xs text-slate-600 font-mono truncate max-w-32">
            {sessionId.slice(0, 8)}...
          </span>
        )}
      </div>

      {/* No session state */}
      {!sessionId && (
        <div className="flex-1 flex flex-col items-center justify-center text-center gap-4 py-12">
          <span className="text-4xl">💬</span>
          <div>
            <p className="text-slate-300 font-medium">No active session</p>
            <p className="text-slate-500 text-sm mt-1">
              Complete an assessment first to start a contextual conversation.
            </p>
          </div>
        </div>
      )}

      {/* Messages */}
      {sessionId && (
        <>
          <div className="flex-1 overflow-y-auto space-y-4 pr-1 mb-4">
            {messages.map((msg, i) => (
              <MessageBubble
                key={i}
                role={msg.role}
                content={msg.content}
                isStreaming={msg.isStreaming}
              />
            ))}
            <div ref={bottomRef} />
          </div>

          {/* Suggested questions */}
          {messages.length <= 1 && !streaming && (
            <div className="flex flex-wrap gap-2 mb-4">
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  className="text-xs glass px-3 py-1.5 rounded-full text-slate-400
                             hover:text-emerald-300 hover:border-emerald-600/40 transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          )}

          {error && (
            <div className="bg-red-500/10 border border-red-500/25 rounded-xl p-3 text-red-400 text-xs mb-3">
              {error}
            </div>
          )}

          <ChatInput onSend={sendMessage} disabled={streaming || !connected} />
        </>
      )}
    </div>
  )
}
