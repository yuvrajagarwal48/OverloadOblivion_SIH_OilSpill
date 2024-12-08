/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}"], // Adjust paths if necessary
  theme: {
    extend: {
      backgroundImage: {
        'pattern-waves': `linear-gradient(135deg, rgba(0,0,0,0.05) 25%, transparent 25%),
                          linear-gradient(225deg, rgba(0,0,0,0.05) 25%, transparent 25%),
                          linear-gradient(45deg, rgba(0,0,0,0.05) 25%, transparent 25%),
                          linear-gradient(315deg, rgba(0,0,0,0.05) 25%, transparent 25%)`,
        'pattern-hexagon': `linear-gradient(30deg, rgba(0,0,0,0.05) 12%, transparent 12.5%, transparent 87%, rgba(0,0,0,0.05) 87.5%),
                            linear-gradient(150deg, rgba(0,0,0,0.05) 12%, transparent 12.5%, transparent 87%, rgba(0,0,0,0.05) 87.5%),
                            linear-gradient(30deg, rgba(0,0,0,0.05) 12%, transparent 12.5%, transparent 87%, rgba(0,0,0,0.05) 87.5%),
                            linear-gradient(150deg, rgba(0,0,0,0.05) 12%, transparent 12.5%, transparent 87%, rgba(0,0,0,0.05) 87.5%)`,
        'pattern-dots': `radial-gradient(rgba(0,0,0,0.05) 15%, transparent 16%),
                         radial-gradient(rgba(0,0,0,0.05) 15%, transparent 16%)`,
        'pattern-circuit': `linear-gradient(rgba(0,0,0,0.05) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(0,0,0,0.05) 1px, transparent 1px)`,
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        // Add other color configurations here
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        robotoSlab: ['"Roboto Slab"', 'serif'],
        poppins: ['"Poppins"', 'sans-serif'],
        montserrat: ['"Montserrat"', 'sans-serif'],
        philosopher : ['"Philosopher"', 'serif'],
        'sans': ['Manrope', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', "Segoe UI", 'Roboto', "Helvetica Neue", 'Arial', "Noto Sans", 'sans-serif', "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
