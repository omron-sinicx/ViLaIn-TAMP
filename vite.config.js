import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import yaml from '@rollup/plugin-yaml';
import fs from 'fs';
import path from 'path';

const repoName =
  process.env.GITHUB_REPOSITORY?.split('/')[1] ?? path.basename(__dirname);

const templateYaml = fs.readFileSync(
  path.resolve(__dirname, 'template.yaml'),
  'utf8',
);
const theme = templateYaml.match(/^theme:\s*(\S+)/m)?.[1] ?? 'default';
const themeStyles =
  theme === 'dark'
    ? path.resolve(__dirname, 'src/scss/dark-theme.scss')
    : path.resolve(__dirname, 'src/scss/theme.scss');

// https://vite.dev/config/
export default defineConfig({
  base: process.env.NODE_ENV === 'production' ? `/${repoName}/` : './',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@theme-styles': themeStyles,
    },
  },
  plugins: [react(), yaml()],
  build: {
    outDir: 'build',
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html'),
      },
    },
    target: 'es2015',
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    watch: {
      usePolling: true,
      interval: 1000,
      ignored: ['**/node_modules/**', '**/build/**', '**/.git/**']
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        silenceDeprecations: ['import'],
        quietDeps: true,
      },
    },
  },
});
