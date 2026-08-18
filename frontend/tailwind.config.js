/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{vue,js,ts}"],
  darkMode: 'class',
  theme: { extend: { colors: { glass: { DEFAULT:'rgba(255,255,255,0.05)', hover:'rgba(255,255,255,0.1)', border:'rgba(255,255,255,0.1)' }, accent: { DEFAULT:'#6366f1', hover:'#818cf8' }, surface: { DEFAULT:'#0f0f14', raised:'#1a1a24' } } } },
  plugins: []
}
