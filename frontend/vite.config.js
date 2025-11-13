import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  
  // Define environment variables for the build
  // These will be replaced at build time with the actual values
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(
      process.env.VITE_API_URL || 'https://dentaflow-backend-staging-gmi5lyn5wq-uc.a.run.app/api/v1'
    ),
    'import.meta.env.VITE_APP_ENV': JSON.stringify(
      process.env.VITE_APP_ENV || 'production'
    ),
  },
  
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
