/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        space: {
          darkest: '#0B0E17',
          dark: '#121827',
          mid: '#1A1F33',
          accent: '#4E54C8',
          highlight: '#8F94FB',
          glow: '#6A85ED',
          purple: '#3B1B70',
          pink: '#CE5D98',
          star: '#F4EFFF',
        }
      },
      fontFamily: {
        display: ['Rajdhani', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'twinkle': 'twinkle 4s ease-in-out infinite',
        'pulse-slow': 'pulse 8s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 3s ease-in-out infinite alternate',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        twinkle: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(106, 133, 237, 0.5), 0 0 10px rgba(106, 133, 237, 0.2)' },
          '100%': { boxShadow: '0 0 15px rgba(106, 133, 237, 0.8), 0 0 20px rgba(106, 133, 237, 0.4)' }
        }
      },
      backgroundImage: {
        'space-gradient': 'linear-gradient(to bottom, #0B0E17, #121827, #1A1F33)',
        'nebula': 'radial-gradient(circle at 50% 50%, rgba(78, 84, 200, 0.4) 0%, rgba(59, 27, 112, 0.1) 50%, transparent 100%)',
      },
    },
  },
  plugins: [],
};