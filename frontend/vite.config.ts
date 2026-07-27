import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: {
      // 开发期将 /api 代理到后端 FastAPI
      '/api': 'http://localhost:8000',
      // 开发期将 /static 代理到后端，用于加载本地球员头像等静态资源
      '/static': 'http://localhost:8000',
    },
  },
})
