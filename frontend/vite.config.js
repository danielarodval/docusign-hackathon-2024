import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"
import { fileURLToPath } from 'url';

// Manually define 
const __filename = fileURLToPath(import.meta.url); 
const __dirname = path.dirname(__filename)

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve:{
    alias:{
      "@": path.resolve(__dirname)
    }
  },
  server:{
    port:3000,
    cors:true,
    proxy:{
      "/api":{
        target:'http://127.0.0.1:5000',
        changeOrigin:true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      }
    }
  }
})
