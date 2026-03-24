/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
    '../finkit-ui/src/**/*.{js,jsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        gain: '#16a34a',
        loss: '#dc2626',
      },
      fontFamily: {
        sans: 'var(--font-sans)',
        mono: 'var(--font-mono)',
      },
      gridTemplateColumns: {
        12: 'repeat(12, minmax(0, 1fr))',
      },
    },
  },
  plugins: [],
}
