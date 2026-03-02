import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 8080,
    proxy: {
      // 基础模块API - 转发到后端8083
      '/basemodule': {
        target: 'http://localhost:8083',
        changeOrigin: true
      },
      // 模版API - 转发到后端8083
      '/template': {
        target: 'http://localhost:8083',
        changeOrigin: true
      },
      // 模版数据API - 转发到后端8083
      '/templateData': {
        target: 'http://localhost:8083',
        changeOrigin: true
      },
      // 其他API - 转发到后端8083
      '/api': {
        target: 'http://localhost:8083',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
