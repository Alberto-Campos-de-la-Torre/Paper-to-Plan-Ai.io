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
        primary: "var(--color-primary)",
        "background-light": "var(--color-bg-light)",
        "background-dark": "var(--color-bg-dark)",
        "surface-light": "var(--color-surface-light)",
        "surface-dark": "var(--color-surface-dark)",
        "border-light": "var(--color-border-light)",
        "border-dark": "var(--color-border-dark)",
        "text-light": "var(--color-text-light)",
        "text-dark": "var(--color-text-dark)",
        "text-secondary-light": "var(--color-text-secondary-light)",
        "text-secondary-dark": "var(--color-text-secondary-dark)",
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
