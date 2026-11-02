import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          DEFAULT: "#1E4D2B",
          dark: "#14371E",
          hover: "#255F35",
          light: "#2D6A4F",
          pale: "#EBF3EC",
        },
        sand: {
          bg: "#FAF9F5",
          card: "#FFFFFF",
          border: "#D1D9D1",
        },
        dashboard: {
          bg: "#F4F7F4",
        },
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
