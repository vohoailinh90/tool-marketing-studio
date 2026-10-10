import path from 'node:path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// `npm run dev` proxies the API to `python app.py --dev` (port 8765); `npm run build`
// writes web/dist, which app.py serves. The built dist is committed so users need no Node.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    proxy: { '/api': 'http://127.0.0.1:8765', '/files': 'http://127.0.0.1:8765' },
  },
})
