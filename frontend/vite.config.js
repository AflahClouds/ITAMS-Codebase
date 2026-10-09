import { defineConfig } from 'vite'
import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'

// https://vite.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    react(),
    // The React Compiler preset is a build-time optimization delivered through a
    // rolldown plugin, which does not run in Vitest's transform pipeline — leaving test
    // files without the automatic JSX runtime. It is not needed to test behavior, so it
    // is applied only outside test runs.
    ...(mode === 'test' ? [] : [babel({ presets: [reactCompilerPreset()] })]),
  ],
  // Only under Vitest. Its transform pipeline honours this and needs it to give test
  // files the automatic JSX runtime; the production build uses oxc, which ignores the
  // option and prints a notice about it on every run. Scoping it keeps both quiet and
  // correct.
  ...(mode === 'test' ? { esbuild: { jsx: 'automatic' } } : {}),
  test: {
    // B9 and B1 both carry requirements about what a person sees. Without a runner
    // those were unverifiable in principle rather than merely untested — a third of the
    // requirement set in docs/conformance/traceability-map.md sat in that state.
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
    include: ['src/**/*.test.jsx'],
    server: {
      // MUI reaches into react-transition-group by directory, which Node's ESM
      // resolver rejects. Inlining lets Vite resolve it the way the browser build does.
      deps: { inline: [/@mui/, /react-transition-group/] },
    },
  },
}))
