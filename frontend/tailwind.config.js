/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Palette alignée avec le site pédagogique APOCAL'IPSSI
        indigo: {
          950: '#1E1B4B',
        },
        amber: {
          DEFAULT: '#F59E0B', // signature ambre apocalyptique
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [],
};
