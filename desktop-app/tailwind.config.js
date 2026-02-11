/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                'medical-green': {
                    50: '#f0f5f0',
                    100: '#dce8dc',
                    200: '#b5d1b5',
                    300: '#8bb98b',
                    400: '#5e9e5e',
                    500: '#3d7a3d',
                    600: '#2d5a2d',
                    700: '#2d3b2d',
                    800: '#1e2a1e',
                    900: '#111a11',
                },
                'medical-cream': {
                    50: '#fdfcfa',
                    100: '#faf8f5',
                    200: '#f5f3ee',
                    300: '#ede9e0',
                    400: '#d4cfc7',
                    500: '#b8b0a4',
                    600: '#8a8178',
                },
                'medical-gold': {
                    50: '#faf6f0',
                    100: '#f0e8d8',
                    200: '#e0d0b0',
                    300: '#c4a87a',
                    400: '#a68b6b',
                    500: '#8b7355',
                    600: '#6b5740',
                },
                'medical-olive': {
                    50: '#f4f5f0',
                    100: '#e5e8dd',
                    200: '#c8ceb8',
                    300: '#a5af8e',
                    400: '#7d8a65',
                    500: '#5e6a48',
                    600: '#444e34',
                },
            },
            fontFamily: {
                display: ['Cormorant Garamond', 'Georgia', 'serif'],
                body: ['DM Sans', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
                brand: ['Poppins', 'DM Sans', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
