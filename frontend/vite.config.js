import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 你的后端服务器
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api') // 确保 /api 前缀被保留
      }
    }
  }
})
