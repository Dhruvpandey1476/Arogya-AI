// Vite config: React plugin + dev-server proxy to the FastAPI backend on :8000.
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/assess': 'http://localhost:8000',
      '/voice': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    }
  }
})
