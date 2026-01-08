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

    async def generate_ai_renders(self, project_id: str, wireframes: List[Dict], idea_description: str):
        """
        Generates high-fidelity images for each screen using the LLM's image generation capability (DALL-E 3).
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
            
            # Prepare key elements string
            components = wf.get('components', [])
            labels = [c.get('label', c.get('type')) for c in components]
            key_elements_str = ', '.join(labels[:8])

            # Construct a prompt that enforces the requested premium style
            prompt = f"""
            High fidelity UI design of a {screen_name} screen for an application described as: "{idea_description}".
            
            Layout Hints (based on structure):
            - Layout: {wf.get('layout_type', 'Standard Web Layout')}
            - Key Elements: {key_elements_str}
            
            Visual Style:
            - Modern, clean, and professional UI.
            - Focus on clarity and usability.
            - Harmonious color palette suitable for {idea_description}.
            
            This must be a polished, final production-ready UI mock-up.
            """
            
            print(f"AIDesigner: Requesting Image Gen for '{screen_name}'...")
            try:
                # 1. Generate URL
                image_url = await self.llm.generate_image(prompt)
                
                if image_url:
                    print(f"AIDesigner: Downloading image for {screen_name}...")
                    
                    # 2. Download Bytes (Using new dep-free method)
                    image_bytes = await self.llm.download_image_bytes(image_url)
                    
                    if image_bytes:
                        file_path = ui_dir / f"{s_filename}.png"
                        with open(file_path, "wb") as f:
                            f.write(image_bytes)
                        print(f"AIDesigner: SUCCESS - Saved High-Fi image to {file_path}")
                    else:
                        print(f"AIDesigner: Download returned empty bytes for {screen_name}")
                else:
                     print(f"AIDesigner: No URL returned for {screen_name}")
            except Exception as e:
                print(f"AIDesigner: Image Gen failed for {screen_name}: {e}")

    def _clean_json(self, text: str) -> str:
        text = re.sub(r"```json\s*", "", text)
        text = re.sub(r"```\s*$", "", text)
        text = re.sub(r"```", "", text)
        return text.strip()
