/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#33bbcf", // from screen 2
        "background-light": "#e0e7ff", // from screen 1 & 2
        "background-dark": "#0c0a1a", // from screen 2
        "surface-light": "#ffffff", // from screen 1
        "surface-dark": "#1a1b26", // from screen 1
        "border-light": "#d1d5db", // from screen 1
        "border-dark": "#4b5563", // from screen 1
        "text-light": "#1f2937", // from screen 1
        "text-dark": "#e5e7eb", // from screen 1
        "text-secondary-light": "#6b7280", // from screen 1
        "text-secondary-dark": "#9ca3ad", // from screen 1
      },
      fontFamily: {
        display: ["Orbitron", "sans-serif"], // from screen 1
        body: ["Roboto", "sans-serif"], // from screen 1 & 3
        mono: ["Roboto Mono", "monospace"], // from screen 2
      },
      borderRadius: {
        DEFAULT: "0.25rem", // from screen 2 & 3
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
