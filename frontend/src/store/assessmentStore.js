import { create } from 'zustand'

const useAssessmentStore = create((set) => ({
  // Assessment results
  sessionId: null,
  diseases: [],
  severity: null,
  cvResult: null,
  explanation: '',
  firstAidSteps: [],
  specialist: '',
  sources: [],
  disclaimer: '',
  isLoading: false,
  error: null,

  // Input state
  selectedSymptoms: [],
  symptomText: '',
  durationDays: 1,
  painScale: 0,
  fever: false,
  feverTemp: '',
  age: 25,
  imageBase64: null,
  imagePreview: null,

  // Actions
  setResult: (result) => set({
    sessionId: result.session_id,
    diseases: result.diseases || [],
    severity: result.severity,
    cvResult: result.cv_result,
    explanation: result.explanation,
    firstAidSteps: result.first_aid_steps || [],
    specialist: result.specialist,
    sources: result.sources || [],
    disclaimer: result.disclaimer,
    error: null,
  }),

  setLoading: (v) => set({ isLoading: v }),
  setError: (e) => set({ error: e, isLoading: false }),

  toggleSymptom: (symptom) => set((state) => ({
    selectedSymptoms: state.selectedSymptoms.includes(symptom)
      ? state.selectedSymptoms.filter((s) => s !== symptom)
      : [...state.selectedSymptoms, symptom],
  })),

  removeSymptom: (symptom) => set((state) => ({
    selectedSymptoms: state.selectedSymptoms.filter((s) => s !== symptom),
  })),

  setSymptomText: (v) => set({ symptomText: v }),
  setDurationDays: (v) => set({ durationDays: v }),
  setPainScale: (v) => set({ painScale: v }),
  setFever: (v) => set({ fever: v }),
  setFeverTemp: (v) => set({ feverTemp: v }),
  setAge: (v) => set({ age: v }),
  setImageBase64: (b64) => set({ imageBase64: b64 }),
  setImagePreview: (url) => set({ imagePreview: url }),

  reset: () => set({
    selectedSymptoms: [], symptomText: '', durationDays: 1,
    painScale: 0, fever: false, feverTemp: '', age: 25,
    imageBase64: null, imagePreview: null,
    diseases: [], severity: null, cvResult: null,
    explanation: '', firstAidSteps: [], specialist: '',
    sources: [], sessionId: null, error: null,
  }),
}))

export default useAssessmentStore
