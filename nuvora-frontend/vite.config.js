import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
  server: {
    allowedHosts: ['nuvora'],
    proxy: {
      '/api': {
        target: 'https://nuvora',
        changeOrigin: true,
        secure: false,
      }
    }
  },
});
