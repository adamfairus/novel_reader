/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        serif: ['Newsreader', 'Georgia', 'Cambria', 'serif'],
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        obsidian: {
          950: '#07090e',
          900: '#0c0f17',
          850: '#111520',
          800: '#181e2b',
          700: '#232b3d',
          600: '#344059',
          300: '#94a3b8',
          100: '#e2e8f0',
        },
        sepia: {
          bg: '#fbf0d9',
          card: '#f4e5c5',
          border: '#e4d2ad',
          text: '#433422',
          muted: '#7a654c',
          heading: '#2c2216',
        },
      },
      maxWidth: {
        measure: '72ch', // 65-75ch optimal reading measure from Impeccable Craft Floor
      },
    },
  },
  plugins: [],
};
