import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    // The React and Tailwind plugins are both required for Make, even if
    // Tailwind is not being actively used – do not remove them
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      // Alias @ to the src directory
      '@': path.resolve(__dirname, './src'),
    },
  },

  // File types to support raw imports. Never add .css, .tsx, or .ts files to this.
  assetsInclude: ['**/*.svg', '**/*.csv'],
  server: {
    port: 4000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8010',
        changeOrigin: true,
        timeout: 300000,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/ai-api': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        timeout: 300000,
        rewrite: (path) => path.replace(/^\/ai-api/, '/api/v1'),
      }
    }
  }
})
