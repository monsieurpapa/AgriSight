import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh
      fastRefresh: true,
    }),
    tailwindcss()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    // Development server configuration
    port: 5173,
    strictPort: false,
    // Disable HMR in Docker/remote environments
    hmr: process.env.HMR === 'false' ? false : undefined,
  },
  build: {
    // Production build configuration
    outDir: 'dist',
    assetsDir: 'assets',
    
    // Code splitting configuration
    rollupOptions: {
      output: {
        // Manual chunk configuration for better caching
        manualChunks: {
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['lucide-react'],
          'vendor-forms': ['react-hook-form'],
          'vendor-queries': ['@tanstack/react-query'],
          'vendor-other': ['axios', 'clsx', 'class-variance-authority'],
        },
      },
    },
    
    // Optimize build performance
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console.log in production
        passes: 2,
      },
      format: {
        comments: false, // Remove comments
      },
    },
    
    // CSS code splitting
    cssCodeSplit: true,
    
    // Source maps for production (disable for smaller bundle)
    sourcemap: false,
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    
    // Module preload polyfill
    modulePreload: {
      polyfill: true,
    },
    
    // Report compressed size
    reportCompressedSize: true,
    
    // CommonJS options
    commonjsOptions: {
      transformMixedEsModules: true,
    },
  },
  
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'axios',
      '@tanstack/react-query',
      'lucide-react',
    ],
    exclude: [],
  },
  
  // Performance hints
  define: {
    __DEV__: `JSON.stringify(${process.env.NODE_ENV === 'development'})`,
  },
})
