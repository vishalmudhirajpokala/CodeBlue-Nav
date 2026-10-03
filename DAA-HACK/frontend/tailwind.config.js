/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        emergency: "#ff4757",
        ward: "#4ecdc4",
        junction: "#ffe66d",
      }
    },
  },
  plugins: [],
}