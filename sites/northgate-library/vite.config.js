import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue()],
  server: { port: 3102, strictPort: true },
  preview: { port: 3102, strictPort: true },
})
