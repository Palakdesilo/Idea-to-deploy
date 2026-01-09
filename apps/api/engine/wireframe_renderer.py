from typing import Dict, List, Any
import re

class WireframeRenderer:
    def __init__(self):
        self.base_css = """
/* Reset & Base */
* { box-sizing: border-box; margin: 0; padding: 0; }
    background-color: #f8f9fa; 
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    display: flex;
    justify-content: center;
    padding: 20px;
    color: #1a1a1a;
}


/* Canvas */
.wireframe-canvas {
    width: 1440px;
    height: 900px; /* Default minimum height */
    background-color: #ffffff;
    position: relative;
    border: 2px solid #000;
    overflow: hidden; /* Clip content outside 1440px */
}


/* Generic Component Styling */
.wf-component {
    position: absolute; /* Absolute positioning as requested */
    border: 2px solid #000; /* Visible borders */
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    font-size: 14px;
    color: #000;
    z-index: 10;
}

/* Component Types */
.wf-type-text {
    border: none;
    background: transparent;
    justify-content: flex-start;
    padding: 4px;
    font-weight: bold;
}
.wf-type-input {
    background: #fff;
    border: 2px solid #000;
    justify-content: flex-start;
    padding-left: 8px;
    color: #666;
}
.wf-type-button {
    background: #fff;
    border: 2px solid #000;
    font-weight: bold;
}
.wf-type-table {
    display: block;
    background: #fff;
}
.wf-type-table .row {
    border-bottom: 1px solid #000;
    height: 32px;
}
.wf-type-card {
    background: #fff;
}
.wf-type-image {
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #000;
}
.wf-type-image::after {
    content: '[IMAGE]';
}

/* Layout Zones */
.wf-header { border-bottom: 2px solid #000; background: #fff; z-index: 5; }
.wf-sidebar { border-right: 2px solid #000; background: #fff; z-index: 5; }
.wf-footer { border-top: 2px solid #000; background: #fff; z-index: 5; }
"""

    def render_project(self, project_id: str, wireframes_json: List[Dict[str, Any]]):
        from .project_manager import ARTIFACTS_DIR
        output_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "html"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Write CSS
        with open(output_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(self.base_css)
            
        screens = []
        for wf in wireframes_json:
            html = self.generate_html(wf)
            # Use screen_name for filename, sanitize it
            import re
            cleaned_name = re.sub(r'[\\/*?:"<>|]', "", wf.get("screen_name", "screen"))
            screen_name = cleaned_name.replace(" ", "_").lower()
            filename = f"{screen_name}.html"
            
            with open(output_dir / filename, "w", encoding="utf-8") as f:
                f.write(html)
                
            screens.append({
                "name": wf.get("screen_name"),
                "file": filename
            })

    def render_premium(self, project_id: str, wireframe: Dict[str, Any], custom_css: str = ""):
        """
        Renders a single wireframe in 'Premium' mode for high-fidelity renders.
        """
        from .project_manager import ARTIFACTS_DIR
        output_dir = ARTIFACTS_DIR / project_id / "designs" / "wireframes" / "premium"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cleaned_name = re.sub(r'[\\/*?:"<>|]', "", wireframe.get("screen_name", "screen"))
        screen_name = cleaned_name.replace(" ", "_").lower()
        
        # Write custom CSS
        css_filename = f"{screen_name}_premium.css"
        with open(output_dir / css_filename, "w", encoding="utf-8") as f:
            f.write(custom_css or self.base_css)
            
        html = self.generate_html(wireframe, css_file=css_filename, is_premium=True)
        html_filename = f"{screen_name}_premium.html"
        
        with open(output_dir / html_filename, "w", encoding="utf-8") as f:
            f.write(html)
        
        return output_dir, html_filename


    def generate_html(self, wf: Dict[str, Any], css_file: str = "style.css", is_premium: bool = False) -> str:

        screen_name = wf.get("screen_name", "Wireframe")
        
        # 1. Parse Dimensions
        canvas = wf.get("canvas_size", {"width": 1440, "height": 900})
        cw, ch = canvas.get("width", 1440), canvas.get("height", 900)
        
        # 2. Layout Elements (Header/Sidebar/Footer) -> Rendered as absolute divs
        layout_html = ""
        
        header = wf.get("header", {})
        if header and header.get("height", 0) > 0:
            h_h = header.get("height")
            layout_html += f'<div class="wf-component wf-header" style="top:0; left:0; width:{cw}px; height:{h_h}px;"></div>'

        sidebar = wf.get("sidebar", {})
        if sidebar and sidebar.get("width", 0) > 0:
            s_w = sidebar.get("width")
            # Assuming sidebar typically starts below header if header exists, but prompt says "Sections with absolute positions"
            # We will rely on the absolute positions given in 'components' effectively, 
            # BUT structural blocks (Header/Sidebar) might be separate. 
            # Let's render them as backgrounds if they are structural zones.
            # If the user JSON provides explicit y, use it. Assuming sidebar is full height or below header.
            # Simplified: Render sidebar at left:0.
            top = header.get("height", 0)
            layout_html += f'<div class="wf-component wf-sidebar" style="top:{top}px; left:0; width:{s_w}px; height:{ch-top}px;"></div>'

        footer = wf.get("footer", {})
        if footer and footer.get("height", 0) > 0:
            f_h = footer.get("height")
            layout_html += f'<div class="wf-component wf-footer" style="bottom:0; left:0; width:{cw}px; height:{f_h}px;"></div>'

        # 3. Components
        components_html = ""
        for comp in wf.get("components", []):
            c_type = comp.get("type", "text").lower()
            x = comp.get("x", 0)
            y = comp.get("y", 0)
            w = comp.get("width", 100)
            h = comp.get("height", 40)
            label = comp.get("label", "")
            
            # Map type to class
            css_class = f"wf-type-{c_type}" if c_type in ["text", "input", "button", "table", "card", "image"] else "wf-component"
            
            content = label
            if c_type == "input":
                content = f'<span style="opacity:0.5">{label}</span>'
            
            components_html += f'''
                <div class="{css_class} wf-component" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px;">
                    {content}
                </div>
            '''

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen_name}</title>
    {"<link rel='preconnect' href='https://fonts.googleapis.com'><link rel='preconnect' href='https://fonts.gstatic.com' crossorigin><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>" if is_premium else ""}
    <link rel="stylesheet" href="{css_file}">
</head>
<body>
    <div class="wireframe-canvas" style="width:{cw}px; height:{ch}px; border: { 'none; box-shadow: 0 10px 30px rgba(0,0,0,0.1)' if is_premium else '2px solid #000' }">
        {layout_html}
        {components_html}
    </div>
</body>
</html>
"""

