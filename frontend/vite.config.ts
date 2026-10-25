import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// Configuración de Vite con React y Tailwind CSS v4.
export default defineConfig({
  plugins: [react(), tailwindcss()],
});
