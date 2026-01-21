import os
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Any, Dict
from .llm_service import LLMService
from .project_manager import ARTIFACTS_DIR
from .wireframe_renderer import WireframeRenderer
import uuid
# REMOVED: import requests (Removed dependency to avoid silent failures)

class AIDesigner:
    def __init__(self):
        self.llm = LLMService()
        self.renderer = WireframeRenderer()

    async def generate_visuals(self, project_id: str, idea_description: str) -> List[Any]:
        print(f"AIDesigner: Starting visual design generation for {project_id}")
        
        # 1. Screen List Generation (Existing Logic)
        docs_dir = ARTIFACTS_DIR / project_id / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        screen_list_path = docs_dir / "screen_list.txt"

        if not screen_list_path.exists():
            prompt = f"""want to Build "{idea_description}"

Give me a page list and structural component-based wireframe descriptions.
Focus on layout and functional elements (Header, Sidebar, Grid, Form).
Do NOT include visual style descriptions (no colors, shadows, or 3d effects).
generate png design"""

            print("AIDesigner: Requesting design structure from LLM...")
            result = await self.llm.generate_content("DESIGN_DOC", {"idea": idea_description}, prompt)
            
            with open(screen_list_path, "w", encoding="utf-8") as f:
                f.write(result)
        else:
            print("AIDesigner: Screen list already exists.")

        # 2. Wireframe Generation
        wireframes = await self.produce_wireframes(project_id)
        
        # 3. High Fidelity Image Generation
        if wireframes:
            await self.generate_ai_renders(project_id, wireframes, idea_description)
        
        # 4. Collect Results for UI
        visuals = []
        
        # A. Collect Wireframes
        wf_img_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "images"
        if wf_img_dir.exists():
            for img_file in wf_img_dir.glob("*.png"):
                stem = img_file.stem
                if "_design" in stem: continue 
                
                base_name = stem.replace("_", " ").title()
                visuals.append({
                    "id": str(uuid.uuid4()),
                    "title": f"{base_name} (Wireframe)",
                    "screenName": base_name, 
                    "description": "Low-fidelity structural wireframe",
                    "imageUrl": f"/api/projects/{project_id}/wireframes/{img_file.name}",
                    "localPath": str(img_file.absolute()),
                    "type": "wireframe"
                })

        # B. Collect High-Fidelity UI from ui/ folder
        ui_img_dir = ARTIFACTS_DIR / project_id / "ui"
        if ui_img_dir.exists():
             for img_file in ui_img_dir.glob("*.png"):
                stem = img_file.stem
                base_name = stem.replace("_", " ").title()
                
                visuals.append({
                    "id": str(uuid.uuid4()),
                    "title": f"{base_name} (High-Fidelity)",
                    "screenName": base_name, 
                    "description": "High-fidelity production ready UI",
                    "imageUrl": f"/api/projects/{project_id}/ui/{img_file.name}",
                    "localPath": str(img_file.absolute()),
                    "type": "ui"
                })
        
        # Sort so Wireframe comes before Design for each screen
        visuals.sort(key=lambda x: x["screenName"])
        
        print(f"AIDesigner: Returning {len(visuals)} visuals to API.")
        return visuals

    async def produce_wireframes(self, project_id: str) -> List[Dict]:
        print(f"AIDesigner: Producing wireframe JSONs for {project_id}")
        docs_dir = ARTIFACTS_DIR / project_id / "docs"
        screen_list_path = docs_dir / "screen_list.txt"
        
        if not screen_list_path.exists():
            print("Error: Screen list missing.")
            return []

        with open(screen_list_path, "r", encoding="utf-8") as f:
            screen_list_content = f.read()

        # Prompt for JSON
        prompt = f"""
        Based on this screen list:
        {screen_list_content}

        Generate a wireframe JSON for EACH screen.
        Output a single pure JSON list of objects.

        Strict JSON Schema per screen:
        {{
            "screen_name": "String (e.g. Home, Dashboard)",
            "canvas_size": {{ "width": 1440, "height": 900 }},
            "layout_type": "single | two-column | grid",
            "header": {{ "height": 80 }},
            "sidebar": {{ "width": 250 }},
            "footer": {{ "height": 100 }},
            "components": [
                {{
                    "type": "text | input | button | table | card | image",
                    "x": Integer (absolute x pos),
                    "y": Integer (absolute y pos),
                    "width": Integer,
                    "height": Integer,
                    "label": "String (content/label)"
                }}
            ]
        }}

        Rules:
        1. Canvas is 1440x900.
        2. Use 8px grid logic for positions.
        3. Do NOT output markdown code blocks. Just the raw JSON array.
        4. Ensure strictly valid JSON.
        """

        print("AIDesigner: Requesting JSON wireframes from LLM...")
        json_str = await self.llm.generate_content("WIREFRAME_JSON", {}, prompt)
        
        # Clean Markdown if present
        json_str = self._clean_json(json_str)

        try:
            wireframes = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"AIDesigner: JSON Generation Failed: {e}")
            print(f"Debug Content: {json_str[:500]}...")
            return []

        # Save JSONs
        json_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "json"
        json_dir.mkdir(parents=True, exist_ok=True)

        for wf in wireframes:
            if not wf: continue
            raw_name = wf.get("screen_name", "screen")
            # Sanitize: replace non-alphanumeric chars (except space/hyphen) with nothing, then underscores
            s_name = re.sub(r'[\\/*?:"<>|]', "", raw_name) 
            s_name = s_name.replace(" ", "_").lower()
            with open(json_dir / f"{s_name}.json", "w", encoding="utf-8") as f:
                json.dump(wf, f, indent=2)

        # 3. Render HTML
        print("AIDesigner: Rendering HTML...")
        self.renderer.render_project(project_id, wireframes)

        # 4. Render Images (Playwright)
        html_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "html"
        img_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "images"
        
        print("AIDesigner: Capturing Screenshots (structural base)...")
        script_path = Path(__file__).parent / "screenshot_capture.py"
        try:
            subprocess.run([sys.executable, str(script_path), str(html_dir), str(img_dir)], check=True)
            print("AIDesigner: formatting completed.")
        except subprocess.CalledProcessError as e:
            print(f"AIDesigner: Screenshot capture failed: {e}")

        return wireframes

    def _describe_wireframe_structure(self, wf: Dict) -> str:
        """
        Creates a natural language description of the wireframe structure to guide the image generator.
        """
        parts = []
        
        # 1. Macro Layout
        header = wf.get("header") or {}
        header_h = header.get("height", 0)
        
        sidebar = wf.get("sidebar") or {}
        sidebar_w = sidebar.get("width", 0)
        
        parts.append(f"Layout Structure: {wf.get('layout_type', 'standard')}.")
        if header_h > 0:
            parts.append("Has a top navigation header.")
        if sidebar_w > 0:
            parts.append("Has a left-side vertical navigation sidebar.")
            
        # 2. Components Structure
        components = wf.get("components") or []
        if not components:
            return " ".join(parts)

        # Describe significant components
        parts.append("Page Content:")
        # Sort top-to-bottom
        sorted_comps = sorted(components, key=lambda c: c.get("y", 0) if c else 0)
        
        for c in sorted_comps[:15]: # Limit to top 15 elements to avoid overwhelming prompt
            ctype = c.get("type", "element")
            label = c.get("label", "")
            
            # Simple spatial context
            x = c.get("x", 0)
            y = c.get("y", 0)
            
            location = "central area"
            if y < header_h + 50: location = "top area"
            elif sidebar_w > 0 and x < sidebar_w + 50: location = "sidebar"
            
            desc = f"A {ctype}"
            if label:
                desc += f" labeled '{label}'"
            desc += f" located in the {location}."
            parts.append(desc)
            
        return "\n".join(parts)

    async def generate_ai_renders(self, project_id: str, wireframes: List[Dict], idea_description: str):
        """
        Generates high-fidelity images for each screen using the LLM's image generation capability.
        Saves as distinct files in the 'ui' folder.
        """
        print(f"AIDesigner: Generating High-Fidelity AI Images for {project_id}...")
        
        # New separate folder for High-Fidelity UI
        ui_dir = ARTIFACTS_DIR / project_id / "ui"
        ui_dir.mkdir(parents=True, exist_ok=True)
        
        for wf in wireframes:
            screen_name = wf.get("screen_name", "Screen")
            # Sanitize filename
            clean_name = re.sub(r'[\\/*?:"<>|]', "", screen_name)
            s_filename = clean_name.replace(" ", "_").lower()
            
            # Generate detailed structural description
            structure_description = self._describe_wireframe_structure(wf)

            # Construct a prompt that enforces the requested premium style AND structure
            prompt = f"""
            Design a High-Fidelity, Production-Ready UI Mockup for: {screen_name}.
            App Description: "{idea_description}"
            
            STRICT LAYOUT INSTRUCTIONS (Must match exactly):
            {structure_description}
            
            VISUAL STYLE:
            - Aesthetics: Very Modern, Premium, Clean, Professional.
            - Tech Stack Feel: React/Tailwind, Glassmorphism elements.
            - Color Palette: Harmonious and suitable for the brand.
            - Typography: Readable, sleek sans-serif.
            
            The output must look like a real screenshot of a finished application, perfectly matching the described layout structure.
            """
            
            print(f"AIDesigner: Requesting High-Fidelity Render for '{screen_name}'...")
            
            # FORCE CODE-TO-IMAGE RENDER (User Preference: "Best Image Ever")
            # We skip direct image generation because it is unreliable (404s) and less consistent than code-based rendering.
            await self.generate_code_render_fallback(project_id, wf, idea_description, s_filename)

    async def generate_code_render_fallback(self, project_id: str, wireframe: Dict[str, Any], idea_description: str, filename: str):
        """
        FALLBACK: Generates a high-fidelity 'Proper UI' by asking the LLM to write a 
        complete, premium Tailwind HTML version of the wireframe.
        """
        print(f"AIDesigner: Generating High-Fidelity UI Fallback (Code-to-Image) for {filename}...")
        
        screen_name = wireframe.get("screen_name", "Screen")
        
        # We pass the WHOLE wireframe JSON so the LLM knows exactly where everything goes
        wf_json_str = json.dumps(wireframe, indent=2)
        
        prompt = f"""
        Act as a Lead UI/UX Engineer. Your task is to transform a wireframe JSON into a **Premium, Production-Ready UI Mockup**.
        
        Project: "{idea_description}"
        Screen: {screen_name}
        
        Wireframe Structural Data:
        {wf_json_str}
        
        CRITICAL CONSISTENCY RULES:
        1. **Dynamic Brand Identity**: 
           - Analyze the Project Description: "{idea_description}" to determine the SINGLE best fitting Color Palette.
           - (e.g. Construction -> Orange/Black, EdTech -> Blue/White, Gaming -> Dark/Neon).
           - Use this selected palette strictly and consistently.
        2. **Smart Contrast & Theme**: 
           - Decide if "Dark Mode" or "Light Mode" fits the industry best.
           - Ensure High Contrast (e.g., if Dark Mode, use light/white text).
        3. **Global Components**: 
           - If the JSON includes a 'sidebar', you MUST render a visible, permanent Left Sidebar (width ~250px). Do NOT hide it behind a menu.
           - If the JSON includes a 'header', you MUST render a top Navigation Header.
           - These global components must look IDENTICAL in style across every single page you generate.
        4. **Layout Fidelity**: Follow the x/y positions in the JSON as a strict guide for where major sections belong.
        
        GUIDELINES:
        - Aesthetics: Ultra-modern SaaS, Clean, High-Contrast, Professional.
        - Tech: Tailwind CSS (use CDN), Lucide Icons (use CDN), Google Fonts (Inter, Plus Jakarta Sans).
        - **Visual Style**: Use glassmorphism (`backdrop-blur`) for sticky headers/sidebars. Deep shadows (`shadow-xl`) for cards.
        - **Imagery**: You MUST use `https://images.unsplash.com/...` URLs with search keywords. 
          - EXAMPLE: `https://images.unsplash.com/photo-1555041469-a586c61ea9bc?auto=format&fit=crop&w=800&q=80` (Furniture)
          - DO NOT USE `source.unsplash.com` (It is broken).
          - DO NOT USE placeholders.
        - **Logo**: Do NOT write the word "LOGO". Create a real looking logo using a relevant Lucide Icon + Styled Text (e.g. 🏗️ Constructo).
        - Content: Use REAL professional copy and data.
        
        OUTPUT:
        - Return a SINGLE self-contained HTML file (including Tailwind CDN and styles).
        - Output ONLY the raw HTML code. No markdown code blocks, no explanation.
        """
        
        try:
            # 1. Generate High-Fi HTML
            high_fi_html = await self.llm.generate_content("UI_ENGINEER", {}, prompt)
            high_fi_html = self._clean_json(high_fi_html)
            
            # 2. Save it to the premium folder
            premium_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "premium"
            premium_dir.mkdir(parents=True, exist_ok=True)
            
            html_filename = f"{filename}_highfi.html"
            html_path = premium_dir / html_filename
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(high_fi_html)
            
            # 3. Capture Screenshot
            ui_dir = ARTIFACTS_DIR / project_id / "ui"
            ui_dir.mkdir(parents=True, exist_ok=True)
            
            script_path = Path(__file__).parent / "screenshot_capture.py"
            img_path = ui_dir / f"{filename}.png"
            
            print(f"AIDesigner: Capturing high-fidelity screenshot for {filename}...")
            # Point capture script to the specific premium directory
            subprocess.run([sys.executable, str(script_path), str(premium_dir), str(ui_dir)], check=True)
            
            print(f"AIDesigner: SUCCESS - Proper UI generated via High-Fi fallback for {filename}")
            return True
        except Exception as e:
            print(f"AIDesigner: High-Fi fallback FAILED for {filename}: {e}")
            return False



    def _clean_json(self, text: str) -> str:
        # 1. Remove Markdown code blocks
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*$", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()

        # 2. Extract strictly the JSON array if conversational text exists
        # Find the first '[' and the last ']'
        start_idx = text.find('[')
        end_idx = text.rfind(']')

        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            text = text[start_idx : end_idx + 1]
        
        return text
