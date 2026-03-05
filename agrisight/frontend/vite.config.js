import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'
import { fileURLToPath } from 'url'

import { VitePWA } from 'vite-plugin-pwa'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Enable React Fast Refresh
      fastRefresh: true,
    }),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'mask-icon.svg'],
      manifest: {
        name: 'AgriSight',
        short_name: 'AgriSight',
        description: 'Satellite-driven agricultural monitoring platform',
        theme_color: '#10b981',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/sh\.dataspace\.copernicus\.eu\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'satellite-tiles-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 days
              },
              cacheableResponse: {
                statuses: [0, 200],
              },
            },
          },
          {
            urlPattern: /^\/api\/v1\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24, // 24 hours
              },
              networkTimeoutSeconds: 10,
            },
          },
        ],
      }
    })
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
    minify: false, // Disable minification to debug build failure

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

  // Define removed - was causing esbuild error with JSON.stringify
})
