from pathlib import Path
import shutil

ARTIFACTS_DIR = Path(r"d:\Palak\Idea-to-deploy\apps\api\data\artifacts")
PROJECT_ID = "76ecba6a-60f5-4716-bbf3-a938cc1aa44a"

app_dir = ARTIFACTS_DIR / PROJECT_ID / "code" / "frontend" / "app"
root_page = app_dir / "page.tsx"

if not root_page.exists():
    print("Root page missing. Searching for landing page...")
    
    # Check for possible landing page directories
    candidates = ["landingPage", "landing-page", "home", "Home", "Landing"]
    
    found = None
    for c in candidates:
        candidate_page = app_dir / c / "page.tsx"
        if candidate_page.exists():
            found = candidate_page
            print(f"Found landing page at {c}/page.tsx")
            break
            
    if found:
        # Copy to root
        shutil.copy(found, root_page)
        print(f"Copied {found} to {root_page}")
    else:
        # Create a default root page that links to available pages
        print("No landing page found. Creating index...")
        
        # List other pages
        pages = [p.parent.name for p in app_dir.glob("*/page.tsx")]
        
        links = "\n".join([f'<a href="/{p}" className="text-blue-500 hover:underline capitalize">{p}</a>' for p in pages])
        
        content = f"""import Link from 'next/link';

export default function Home() {{
  return (
    <div className="p-10 flex flex-col gap-4">
      <h1 className="text-2xl font-bold">Index</h1>
      <div className="flex flex-col gap-2">
        {links}
      </div>
    </div>
  )
}}
"""
        with open(root_page, "w") as f:
            f.write(content)
        print("Created index page.")
else:
    print("Root page already exists.")
