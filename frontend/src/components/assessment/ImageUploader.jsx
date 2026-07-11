import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { ImagePlus, X, AlertCircle } from 'lucide-react'
import useAssessmentStore from '../../store/assessmentStore'

export default function ImageUploader() {
  const { imagePreview, setImageBase64, setImagePreview } = useAssessmentStore()

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      const dataUrl = e.target.result
      setImagePreview(dataUrl)
      // Strip the data:image/...;base64, prefix
      const b64 = dataUrl.split(',')[1]
      setImageBase64(b64)
    }
    reader.readAsDataURL(file)
  }, [setImageBase64, setImagePreview])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.webp'] },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
  })

  const clear = (e) => {
    e.stopPropagation()
    setImageBase64(null)
    setImagePreview(null)
  }

  return (
    <div className="flex flex-col items-center gap-4">
      {imagePreview ? (
        <div className="relative w-full max-w-sm">
          <img
            src={imagePreview}
            alt="Uploaded skin"
            className="w-full rounded-2xl object-cover max-h-64 border border-emerald-500/20"
          />
          <button
            onClick={clear}
            className="absolute top-3 right-3 w-8 h-8 bg-slate-900/90 rounded-full flex items-center
                       justify-center text-slate-300 hover:text-red-400 border border-slate-700 transition-colors"
          >
            <X size={14} />
          </button>
          <div className="absolute bottom-3 left-3 bg-slate-900/80 px-3 py-1 rounded-full
                          text-xs text-emerald-400 border border-emerald-500/30 font-mono">
            Image ready for analysis
          </div>
        </div>
      ) : (
        <div
          {...getRootProps()}
          className={`w-full max-w-sm h-48 rounded-2xl border-2 border-dashed flex flex-col items-center
                      justify-center gap-3 cursor-pointer transition-all duration-200
                      ${isDragActive
                        ? 'border-emerald-400 bg-emerald-500/10'
                        : 'border-slate-700 hover:border-emerald-600 hover:bg-emerald-500/5'}`}
        >
          <input {...getInputProps()} />
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20
                          flex items-center justify-center">
            <ImagePlus size={22} className="text-emerald-400" />
          </div>
          <div className="text-center">
            <p className="text-slate-300 text-sm font-medium">
              {isDragActive ? 'Drop image here' : 'Drag & drop or click to upload'}
            </p>
            <p className="text-slate-600 text-xs mt-1">JPG, PNG, WEBP up to 5MB</p>
          </div>
        </div>
      )}

      <div className="flex items-start gap-2 glass rounded-xl p-3 max-w-sm w-full">
        <AlertCircle size={14} className="text-yellow-400 mt-0.5 shrink-0" />
        <p className="text-xs text-slate-400 leading-relaxed">
          Upload a clear, well-lit photo of the affected skin area.
          The AI classifies skin conditions — results are not a medical diagnosis.
        </p>
      </div>
    </div>
  )
}
