import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  // This correctly reads from .env.production during build
  const env = loadEnv(mode, process.cwd(), '')
  
  // Debug: Log environment variables during build
  console.log('=== Vite Build Environment ===');
  console.log('Mode:', mode);
  console.log('VITE_API_URL:', env.VITE_API_URL);
  console.log('VITE_APP_ENV:', env.VITE_APP_ENV);
  console.log('================================');

  return {
    plugins: [react(), tailwindcss()],
    define: {
      // Use loadEnv to read from .env files correctly
      'import.meta.env.VITE_API_URL': JSON.stringify(env.VITE_API_URL || 'http://localhost:8000/api/v1'),
      'import.meta.env.VITE_APP_ENV': JSON.stringify(env.VITE_APP_ENV || 'development'),
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
  }
})
