import axios from 'axios'

// Uses VITE_API_URL when set (production), else localhost for local dev.
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
})

export const assessmentService = {
  async submit(payload) {
    const { data } = await api.post('/assess', payload)
    return data
  },

  async searchSymptoms(query) {
    const { data } = await api.post('/assess/symptom-search', { query, top_k: 10 })
    return data.matched_symptoms || []
  },
}

export const voiceService = {
  async transcribe(audioBlob) {
    const formData = new FormData()
    formData.append('audio', audioBlob, 'recording.wav')
    const { data } = await api.post('/voice', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}

export const healthService = {
  async check() {
    const { data } = await api.get('/health')
    return data
  },
}

export default api
