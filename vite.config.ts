import path from 'node:path'
import ui from '@nuxt/ui/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@/': `${path.resolve(__dirname, 'src')}/`,
    },
  },
  plugins: [
    vue(),
    ui({
      ui: {
        colors: {
          primary: 'green',
          neutral: 'slate',
        },
      },
    }),
  ],
})
