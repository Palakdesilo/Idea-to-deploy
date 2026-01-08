import sys
import os
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    # Do not exit immediately if imported, just warn
    print("Playwright not installed.")
    sync_playwright = None

def capture_screenshots(input_dir_str: str, output_dir_str: str):
    input_dir = Path(input_dir_str)
    output_dir = Path(output_dir_str)
    output_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})

        for html_file in input_dir.glob("*.html"):
            if html_file.name == "index.html": 
                continue # Skip index if present

            print(f"Rendering {html_file.name}...")
            url = f"file://{html_file.absolute()}"
            page.goto(url)
            
            # Additional wait to ensure render
            page.wait_for_timeout(100) 

            screenshot_path = output_dir / f"{html_file.stem}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"Saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python screenshot_capture.py <input_html_dir> <output_png_dir>")
        sys.exit(1)
    
    capture_screenshots(sys.argv[1], sys.argv[2])
