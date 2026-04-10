/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        karbon: {
          50: "#D8F3DC",
          100: "#B7E4C7",
          200: "#95D5B2",
          300: "#74C69D",
          400: "#52B788",
          500: "#40916C",
          600: "#2D6A4F",
          700: "#1B4332",
          800: "#132E22",
          900: "#0B1A13",
        },
      },
    },
  },
  plugins: [],
};
