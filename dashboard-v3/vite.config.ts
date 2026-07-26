import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import { resolve } from 'path'

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        login: resolve(__dirname, 'pages/login/index.html'),
        trading: resolve(__dirname, 'pages/trading/index.html'),
        execution: resolve(__dirname, 'pages/execution/index.html'),
        portfolio: resolve(__dirname, 'pages/portfolio/index.html'),
        markets: resolve(__dirname, 'pages/markets/index.html'),
        research: resolve(__dirname, 'pages/research/index.html'),
        system: resolve(__dirname, 'pages/system/index.html'),
      },
    },
  },
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
