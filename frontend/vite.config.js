import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Let Vite naturally read from .env files - no need for explicit define
  // Vite automatically exposes VITE_* variables to import.meta.env
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
  },
  server: {
    port: 3000,
    strictPort: false,
  },
  preview: {
    port: 3001,
    strictPort: false,
    allowedHosts: 'all',
  },
})
