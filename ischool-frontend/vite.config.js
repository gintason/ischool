// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://www.ischool.ng', // 👈 your Django backend
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
