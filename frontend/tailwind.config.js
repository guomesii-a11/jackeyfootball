import tailwindcssAnimate from 'tailwindcss-animate'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        forward: '#FF5A36',
        midfielder: '#1FB6C9',
        defender: '#2ECC71',
        goalkeeper: '#9B59F6',
        gold: '#FFC53D',
        bg0: '#050608',
        bg1: '#0A0C12',
        bg2: '#11141C',
        ink: '#FFFFFF',
        muted: '#C7CEDB',
      },
      fontFamily: {
        sans: ['PingFang SC', 'Helvetica Neue', 'Microsoft YaHei', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [tailwindcssAnimate],
}
