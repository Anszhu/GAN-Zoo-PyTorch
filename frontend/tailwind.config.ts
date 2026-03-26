import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#111111",
        cream: "#faf5ef",
        ember: "#d55d3f",
        moss: "#6d8b74",
        sand: "#dcc9a7"
      },
      boxShadow: {
        card: "0 20px 60px rgba(17, 17, 17, 0.12)"
      }
    }
  },
  plugins: []
};

export default config;

