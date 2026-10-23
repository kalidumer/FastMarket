import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(), 
  ],
  resolve: {
    alias: {
      // Modern native way to cleanly map '@' to the absolute 'src' folder location
      '@': path.resolve(path.dirname(new URL(import.meta.url).pathname), './src'),
    },
  },
})