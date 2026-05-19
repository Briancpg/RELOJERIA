import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#18211f",
        muted: "#60706b",
        line: "#d9e1de",
        surface: "#f7faf9",
        accent: "#0f766e"
      }
    }
  },
  plugins: []
};

export default config;

