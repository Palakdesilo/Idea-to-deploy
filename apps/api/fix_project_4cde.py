from pathlib import Path
import shutil

ARTIFACTS_DIR = Path(r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts")
PROJECT_ID = "4cde7b0d-2d8a-4c8b-b518-9b29d658ce56"

# 1. Fix app/page.tsx header
page_path = ARTIFACTS_DIR / PROJECT_ID / "code" / "frontend" / "app" / "page.tsx"

if page_path.exists():
    with open(page_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    if lines and (lines[0].strip().startswith("#") or lines[0].strip().startswith("Here is")):
        print(f"Removing header from {page_path}")
        new_content = "".join(lines[1:])
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(new_content)
else:
    print("Page.tsx not found?")

# 2. Fix tailwind config (just in case)
tailwind_path = ARTIFACTS_DIR / PROJECT_ID / "code" / "frontend" / "tailwind.config.ts"
if tailwind_path.exists():
    # Write the good config
    content = """import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
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
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
"""
    with open(tailwind_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed tailwind config.")
