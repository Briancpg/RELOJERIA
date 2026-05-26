import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}", "./types/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        border: "hsl(var(--border))",
        muted: "hsl(var(--muted))",
        accent: "hsl(var(--accent))",
        gold: "hsl(var(--gold))",
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        danger: "hsl(var(--danger))",
        ink: "hsl(var(--foreground))",
        line: "hsl(var(--border))",
        surface: "hsl(var(--surface))"
      },
      boxShadow: {
        glow: "0 0 0 1px hsl(var(--gold) / 0.12), 0 18px 40px hsl(0 0% 0% / 0.25)"
      }
    }
  },
  plugins: []
};

export default config;
