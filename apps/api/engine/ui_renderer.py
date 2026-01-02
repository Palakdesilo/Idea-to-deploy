import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

class UIRenderer:
    def __init__(self):
        self.default_tokens = {
            "palette": {
                "background": "#0F172A",
                "surface": "#1E293B",
                "primary": "#8B5CF6",
                "foreground": "#F8FAFC",
                "accent": "#F472B6"
            }
        }
    
    def _generate_dynamic_theme(self, desc: str):
        # Default Theme (Deep Space - Purple/Pink)
        theme = {
            "name": "default",
            "palette": {
                "background": "#0F172A", "surface": "#1E293B",
                "primary": "#8B5CF6", "accent": "#F472B6", "foreground": "#F8FAFC"
            },
            "gradient_primary": "linear-gradient(135deg, #FF5ACD 0%, #8B5CF6 100%)",
            "bg_gradient": "radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.15) 0%, transparent 20%), radial-gradient(circle at 90% 80%, rgba(255, 90, 205, 0.15) 0%, transparent 20%)",
            "font": "'Outfit', 'Inter', sans-serif",
            "glow": "rgba(139, 92, 246, 0.3)",
            "shadow": "rgba(0,0,0,0.5)"
        }
        
        if any(x in desc for x in ["finance", "bank", "crypto", "security", "corporate", "law", "business"]):
            # Ocean Blue Theme
            theme.update({
                "palette": {"background": "#020617", "surface": "#0F172A", "primary": "#3B82F6", "accent": "#06B6D4", "foreground": "#F8FAFC"},
                "gradient_primary": "linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%)",
                "bg_gradient": "radial-gradient(circle at 10% 20%, rgba(59, 130, 246, 0.15) 0%, transparent 20%), radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.15) 0%, transparent 20%)",
                "font": "'Inter', sans-serif",
                "glow": "rgba(59, 130, 246, 0.3)"
            })
        elif any(x in desc for x in ["health", "eco", "green", "bio", "nature", "plant", "garden", "fitness"]):
            # Emerald Nature Theme
            theme.update({
                "palette": {"background": "#052e16", "surface": "#064e3b", "primary": "#10B981", "accent": "#A7F3D0", "foreground": "#ECFDF5"},
                "gradient_primary": "linear-gradient(135deg, #34D399 0%, #059669 100%)",
                "bg_gradient": "radial-gradient(circle at 15% 25%, rgba(16, 185, 129, 0.15) 0%, transparent 25%), radial-gradient(circle at 85% 75%, rgba(52, 211, 153, 0.15) 0%, transparent 25%)",
                "font": "'Outfit', sans-serif",
                "glow": "rgba(16, 185, 129, 0.3)"
            })
        elif any(x in desc for x in ["orange", "warm", "social", "food", "lifestyle", "creative", "art"]):
            # Sunset Orange Theme
            theme.update({
                "palette": {"background": "#1c1917", "surface": "#292524", "primary": "#F97316", "accent": "#FBBF24", "foreground": "#FAFAF9"},
                "gradient_primary": "linear-gradient(135deg, #FBBF24 0%, #EF4444 100%)",
                "bg_gradient": "radial-gradient(circle at 20% 20%, rgba(249, 115, 22, 0.15) 0%, transparent 25%), radial-gradient(circle at 80% 80%, rgba(239, 68, 68, 0.15) 0%, transparent 25%)",
                "font": "'Outfit', 'Inter', sans-serif",
                "glow": "rgba(249, 115, 22, 0.3)"
            })
            
        return theme

    def render_project(self, project_id: str, wireframes: List[Dict[str, Any]], ui_design: Dict[str, Any], project_name: str = "Project"):
        from .project_manager import ARTIFACTS_DIR
        output_dir = ARTIFACTS_DIR / project_id / "ui"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tokens = ui_design.get("design_tokens", self.default_tokens)
        
        # Determine theme based on project keywords
        desc = (project_name + " " + (ui_design.get("description", ""))).lower()
        theme = self._generate_dynamic_theme(desc)
        
        palette = theme["palette"]
        
        # Premium CSS with Glassmorphism and HSL
        css_template = """
:root {
    --primary: [PRIMARY];
    --bg-color: [BG_COLOR];
    --surface: [SURFACE];
    --accent: [ACCENT];
    --text-primary: [TEXT_PRIMARY];
    --text-secondary: #94A3B8;
    --border-color: rgba(255, 255, 255, 0.08);
    --radius-lg: 24px;
    --radius-md: 16px;
    --shadow-premium: 0 20px 40px -10px [SHADOW_COLOR];
    --font-family: [FONT_FAMILY], sans-serif;
    --glow: 0 0 20px [GLOW_COLOR];
    --glow-text: 0 0 30px [GLOW_COLOR];
    --gradient-primary: [GRADIENT_PRIMARY];
    --gradient-surface: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { 
    background-color: var(--bg-color); 
    font-family: var(--font-family); 
    color: var(--text-primary); 
    line-height: 1.6; 
    overflow-x: hidden;
    background-image: [BG_IMAGE_GRADIENT];
}

.animate-fade { animation: fadeIn 0.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }
.ui-container { max-width: 1280px; margin: 0 auto; padding: 0 40px; }
.glass { background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.05); }
.screen-card { min-height: 100vh; display: flex; flex-direction: column; overflow: hidden; position: relative; }

header { 
    display: flex; justify-content: space-between; align-items: center; 
    padding: 24px 60px; position: absolute; top: 0; left: 0; right: 0; z-index: 100;
}
.logo { font-size: 24px; font-weight: 800; letter-spacing: -0.02em; display: flex; align-items: center; gap: 12px; }
.logo-icon { width: 32px; height: 32px; background: var(--gradient-primary); border-radius: 8px; }

.nav-links { display: flex; gap: 40px; align-items: center; }
.nav-links a { 
    text-decoration: none; color: var(--text-primary); 
    font-weight: 500; font-size: 15px; transition: all 0.3s; opacity: 0.8; 
    position: relative;
}
.nav-links a:hover { opacity: 1; color: var(--accent); }

.section-padding { padding: 100px 0; position: relative; }
.hero-split { display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; min-height: 80vh; }

.grid-layout { display: grid; gap: 32px; }
.grid-cols-12 { grid-template-columns: repeat(12, 1fr); }
.col-span-12 { grid-column: span 12; }
.col-span-8 { grid-column: span 8; }
.col-span-6 { grid-column: span 6; }
.col-span-4 { grid-column: span 4; }
.col-span-3 { grid-column: span 3; }

.card-premium { 
    background: var(--gradient-surface); border-radius: 24px; 
    padding: 40px; border: 1px solid rgba(255,255,255,0.05);
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
    position: relative; overflow: hidden; 
}
.card-premium:hover { transform: translateY(-5px); border-color: rgba(255,255,255,0.1); box-shadow: var(--shadow-premium); }

.btn { 
    padding: 16px 36px; border-radius: 12px; font-weight: 700; 
    text-decoration: none; display: inline-flex; align-items: center; 
    justify-content: center; transition: all 0.3s; cursor: pointer; 
    border: none; font-size: 15px; letter-spacing: 0.01em;
}
.btn-primary { background: var(--gradient-primary); color: white; box-shadow: var(--glow); }
.btn-primary:hover { transform: scale(1.02); filter: brightness(1.1); }
.btn-outline { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: var(--text-primary); }
.btn-outline:hover { background: rgba(255, 255, 255, 0.1); border-color: rgba(255,255,255,0.4); }

.menu-item {
    display: flex; align-items: center; gap: 12px; padding: 12px 16px; 
    border-radius: 12px; text-decoration: none; color: var(--text-primary); 
    font-weight: 600; opacity: 0.5; transition: all 0.2s;
}
.menu-item:hover, .menu-item.active { opacity: 1; background: rgba(255,255,255,0.05); color: var(--primary); }
.menu-item.active { background: rgba(255,255,255,0.05); border-left: 3px solid var(--primary); }

.input-field { background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; color: white; width: 100%; outline: none; transition: 0.3s; }
.input-field:focus { border-color: var(--primary); background: rgba(0,0,0,0.5); }

footer { padding: 100px 0 60px; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2); }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }

/* App Layout Styles */
.app-shell { display: flex; min-height: 100vh; }
.sidebar-menu a {
    display: flex; padding: 14px 20px; border-radius: 12px; color: var(--text-primary); text-decoration: none; font-weight: 600; opacity: 0.6; transition: all 0.2s;
}
.sidebar-menu a:hover, .sidebar-menu a.active {
    background: rgba(255,255,255,0.05); opacity: 1; color: white;
}
.sidebar-menu a.active {
    background: var(--gradient-primary); box-shadow: var(--glow);
    background: var(--gradient-primary); box-shadow: var(--glow); color: var(--text-primary);
}
.top-bar { height: 80px; padding: 0 40px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; }

.avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--accent)); display: flex; align-items: center; justify-content: center; font-weight: 800; }
"""
        css_content = css_template.replace("[PRIMARY]", str(palette.get('primary', '#8B5CF6'))) \
                                  .replace("[BG_COLOR]", str(palette.get('background', '#0F172A'))) \
                                  .replace("[SURFACE]", str(palette.get('surface', palette.get('card_bg', '#1E293B')))) \
                                  .replace("[ACCENT]", str(palette.get('accent', '#F472B6'))) \
                                  .replace("[TEXT_PRIMARY]", str(palette.get('foreground', palette.get('text_main', '#F8FAFC')))) \
                                  .replace("[GRADIENT_PRIMARY]", theme["gradient_primary"]) \
                                  .replace("[BG_IMAGE_GRADIENT]", theme["bg_gradient"]) \
                                  .replace("[FONT_FAMILY]", theme["font"]) \
                                  .replace("[GLOW_COLOR]", theme["glow"]) \
                                  .replace("[SHADOW_COLOR]", theme["shadow"])

        with open(output_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(css_content)

        screens_list = []
        for wf in wireframes:
            try:
                html = self.generate_html(wf, tokens, wireframes, project_name)
                screen_key = wf.get('screenKey', 'screen').lower()
                filename = f"{screen_key}.html"
                with open(output_dir / filename, "w", encoding="utf-8") as f:
                    f.write(html)
                
                screens_list.append({
                    "name": wf.get("screen", screen_key),
                    "url": filename
                })
            except Exception as e:
                print(f"UIRenderer: Error rendering screen {wf.get('screenKey')}: {e}")

        index_html = self.generate_index(screens_list)
        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

    def generate_html(self, wf: Dict[str, Any], tokens: Dict[str, Any], all_screens: List[Dict[str, Any]], project_name: str) -> str:
        screen_name = wf.get("screen", "Screen")
        is_app = any(x in screen_name.lower() for x in ["dashboard", "feed", "profile", "setting", "admin", "analytics", "home", "chat", "list", "detail"]) and "landing" not in screen_name.lower()
        
        nav_map = { s.get("screen", "").lower(): f"{s.get('screenKey', '').lower()}.html" for s in all_screens if s.get("screenKey") }
        nav_map.update({ s.get("screenKey", "").lower(): f"{s.get('screenKey', '').lower()}.html" for s in all_screens if s.get("screenKey") })

        header_links = ""
        sidebar_menu = ""
        
        # Determine logical links
        for s in all_screens[:6]:
            s_key = s.get("screenKey", "").lower()
            active = "active" if s_key == wf.get("screenKey", "").lower() else ""
            link = f'<a href="{s_key}.html" class="{active}">{s.get("screen")}</a>'
            header_links += link
            sidebar_menu += f'<a href="{s_key}.html" class="menu-item {active}">{s.get("screen")}</a>'

        content_html = ""
        for section in wf.get("layout", []):
            s_type = section.get("section", "Main")
            layout_type = section.get("layoutType", "grid")
            
            section_content = ""
            for comp in section.get("components", []):
                section_content += self._render_component(comp, is_app, nav_map)
            
            if not section_content.strip(): continue

            if layout_type == "heroSplit":
                content_html += f'<div class="section-padding"><div class="ui-container hero-split">{section_content}</div></div>'
            elif layout_type == "fullWidth":
                 content_html += f'<div class="section-padding" style="width:100%">{section_content}</div>'
            elif layout_type == "centered" or layout_type == "authShell":
                 # Perfect vertical centering between header and footer
                 content_html += f'<div style="display:flex; align-items:center; justify-content:center; flex: 1; min-height: 70vh; padding: 60px 0;">{section_content}</div>'
            elif layout_type == "masonryGrid":
                 content_html += f'<div class="ui-container section-padding"><div class="grid-layout grid-cols-12" style="gap: 24px;">{section_content}</div></div>'
            else:
                content_html += f'<div class="ui-container section-padding"><div class="grid-layout grid-cols-12">{section_content}</div></div>'

        if is_app:
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen_name} | {project_name}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet">
</head>
<body class="animate-fade">
    <div class="app-shell">
            <aside class="sidebar" style="width: 280px; position: fixed; height: 100vh; background: rgba(15, 23, 42, 0.95); border-right: 1px solid var(--border-color); z-index: 50; padding: 32px;">
                <div class="logo" style="margin-bottom: 60px;">
                    <div class="logo-icon"></div>
                    {project_name[:15].upper()}
                </div>
                <nav class="sidebar-menu" style="display:flex; flex-direction:column; gap:16px;">
                    {sidebar_menu}
                </nav>
                <div style="margin-top: auto; display: flex; align-items: center; gap: 16px; padding-top: 32px; border-top: 1px solid var(--border-color);">
                    <div class="avatar" style="width: 40px; height: 40px; background: var(--gradient-primary); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700;">U</div>
                    <div style="font-size: 14px; font-weight: 700; opacity: 0.8;">User Profile</div>
                </div>
            </aside>
            <main class="app-main" style="margin-left: 280px; padding: 0;">
                <header class="top-bar" style="display: flex; justify-content: space-between; align-items: center; padding: 24px 60px; border-bottom: 1px solid var(--border-color); background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 40;">
                    <h1 style="font-size: 24px; font-weight: 900; letter-spacing: -0.02em;">{screen_name}</h1>
                    <div style="display: flex; gap: 20px; align-items:center;">
                        <div class="btn btn-outline" style="padding: 10px 24px; font-size:13px;">Search Command</div>
                        <div class="btn btn-primary" style="padding: 10px 24px; font-size:13px;">+ New Entry</div>
                    </div>
                </header>
            <div>
                {content_html}
            </div>
        </main>
    </div>
</body>
</html>
"""
        else:
            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen_name} | {project_name}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet">
</head>
<body class="animate-fade">
    <div class="screen-card">
        <header>
             <div class="logo">
                <div class="logo-icon"></div>
                {project_name[:20].upper()}...
             </div>
             <nav class="nav-links">
                {header_links}
                <div class="btn btn-primary">Start Trial</div>
            </nav>
        </header>
        <div>
            {content_html}
        </div>
        <footer>
            <div class="footer-grid ui-container">
                <div>
                    <div class="logo" style="margin-bottom: 24px;">{project_name.upper()}</div>
                    <p style="opacity: 0.6; font-size: 14px;">Next-generation platform for {project_name}.</p>
                </div>
                <div class="footer-col">
                    <h4 style="margin-bottom: 20px; font-size: 12px; text-transform: uppercase;">Product</h4>
                    <p style="font-size: 14px; opacity: 0.6; margin-bottom: 8px;">Discover</p>
                    <p style="font-size: 14px; opacity: 0.6; margin-bottom: 8px;">Network</p>
                    <p style="font-size: 14px; opacity: 0.6;">Intelligence</p>
                </div>
                <div class="footer-col">
                     <h4 style="margin-bottom: 20px; font-size: 12px; text-transform: uppercase;">Connect</h4>
                    <p style="font-size: 14px; opacity: 0.6; margin-bottom: 8px;">Twitter</p>
                    <p style="font-size: 14px; opacity: 0.6; margin-bottom: 8px;">Github</p>
                </div>
                <div class="footer-col">
                     <h4 style="margin-bottom: 20px; font-size: 12px; text-transform: uppercase;">Legal</h4>
                    <p style="font-size: 14px; opacity: 0.6; margin-bottom: 8px;">Privacy</p>
                    <p style="font-size: 14px; opacity: 0.6;">Terms</p>
                </div>
            </div>
        </footer>
    </div>
</body>
</html>
"""

    def _render_component(self, comp: Dict, is_app: bool, nav_map: Dict) -> str:
        import json
        ctype = comp.get("type", "Box").lower()
        label = comp.get("label", "Component")
        content = comp.get("content", "")
        subtext = comp.get("subtext", "")
        sim_data = comp.get("simulated_data", {})
        
        # Link mapping
        link_url = "#"
        if label.lower() in nav_map: link_url = nav_map[label.lower()]

        # Data structure detection
        parsed_data = None
        if isinstance(content, (list, dict)):
            parsed_data = content
        elif isinstance(content, str) and (content.strip().startswith('[') or content.strip().startswith('{')):
            try:
                # Basic cleanup of potentially "dirty" LLM JSON
                clean_content = content.strip().replace("'", '"')
                parsed_data = json.loads(clean_content)
            except:
                pass

        # Heuristic-based type overrides
        l_lower = label.lower()
        if not parsed_data and sim_data:
            parsed_data = sim_data.get("items") or sim_data.get("stats") or sim_data.get("rows")

        # REDUNDANCY FILTER: Skip shell components and obvious placeholders
        # REDUNDANCY FILTER: Skip shell components and obvious placeholders
        l_lower = label.lower()
        
        # Hard skip for Footer/Header/Copyright regardless of content
        # These are handled by the global app shell (lines 284+), so they should NEVER be rendered as components.
        if any(x in l_lower for x in ["footer", "header", "copyright", "nav", "sidebar", "menu", "topbar"]):
            return ""

        # Skip generic "Product" or "Project" boxes that are just placeholders
        if ctype in ["box", "card", "projectcard"] and len(str(content)) < 60 and any(x in l_lower for x in ["product", "project", "dashboard", "analytics"]):
             return ""
        
        # Action detection: If it sounds like a button
        action_keywords = ["save", "update", "delete", "create", "submit", "confirm", "cancel", "apply", "reset", "change", "logout", "signin", "signup", "register", "login"]
        if any(x in l_lower for x in action_keywords) and ctype in ["box", "card", "button"]:
             if len(str(content)) < 150:
                 ctype = "standalone_button"
            
        if any(x in l_lower for x in ["testimonial", "review", "what users say", "trust"]):
            ctype = "testimonials"
        elif any(x in l_lower for x in ["pricing", "plan", "bill"]):
            ctype = "pricing"
        elif any(x in l_lower for x in ["step", "process", "how it works", "flow"]):
            ctype = "steps"
        elif any(x in l_lower for x in ["app", "mobile", "ios", "android", "download", "access"]):
            ctype = "mobile_showcase"
        elif any(x in l_lower for x in ["offer", "join", "community", "feature box"]):
             ctype = "bento_grid"
        elif any(x in l_lower for x in ["overview", "stat", "metric", "performance", "analytic", "traffic", "engagement", "growth", "audience"]):
            ctype = "stats_grid"
        elif any(x in l_lower for x in ["feature", "explore", "benefit"]):
            ctype = "features"
        # Field detection: If it's a small component with a field-like label
        elif ctype in ["box", "card", "input"] and any(x in l_lower for x in ["name", "email", "phone", "password", "address", "city", "zip", "country", "title"]):
            ctype = "field_box"

        if ctype == "hero":
            return f'''
            <div class="col-span-12" style="position: relative; z-index: 2; padding: 80px 0 120px;">
                <div class="hero-split">
                    <div>
                        <h1 style="font-size: 72px; font-weight: 900; margin-bottom: 24px; line-height: 1.1; letter-spacing: -0.04em;">
                            {label} <span class="text-gradient">Platform</span>
                        </h1>
                        <p style="font-size: 20px; opacity: 0.7; margin-bottom: 48px; max-width: 500px; line-height: 1.6;">{content}</p>
                        <div style="display: flex; gap: 16px;">
                            <a href="#" class="btn btn-primary">Get Started ↗</a>
                            <a href="#" class="btn btn-outline">View Demo</a>
                        </div>
                        <div style="margin-top: 48px; display: flex; gap: 32px; opacity: 0.5; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">
                            <span>★ 4.9/5 Rating</span>
                            <span>✓ Free 14-Day Trial</span>
                            <span>♥ Loved by Creators</span>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; transform: rotate(-5deg) translateY(-20px); opacity: 0.8;">
                         <div style="grid-column: span 2; height: 180px; background: rgba(255,255,255,0.05); border-radius: 16px; background-image: url('https://source.unsplash.com/random/600x400/?abstract,tech'); background-size: cover;"></div>
                         <div style="height: 180px; background: rgba(255,255,255,0.05); border-radius: 16px;"></div>
                         <div style="height: 180px; background: rgba(255,255,255,0.05); border-radius: 16px;"></div>
                         <div style="grid-column: span 2; height: 180px; background: var(--gradient-primary); border-radius: 16px; display:flex; align-items:center; justify-content:center; color:white; font-weight:900; font-size:24px;">{label}</div>
                    </div>
                </div>
            </div>
            '''
        elif ctype == "steps":
             items = parsed_data if isinstance(parsed_data, list) else sim_data.get("items", [content or "Step 1", "Step 2", "Step 3"])
             steps_html = ""
             for idx, item in enumerate(items):
                 i_title = item.get("title", f"Step {idx+1}") if isinstance(item, dict) else str(item)
                 i_desc = item.get("description", "Follow this easy process to get started.") if isinstance(item, dict) else "Simple setup process."
                 
                 steps_html += f'''
                 <div class="step-card">
                    <div class="step-icon">{idx+1}</div>
                    <h3 style="font-size: 20px; font-weight: 800; margin-bottom: 12px;">{i_title}</h3>
                    <p style="opacity: 0.6; font-size: 15px; max-width: 250px;">{i_desc}</p>
                 </div>
                 '''
             return f'''
             <div class="col-span-12 section-padding" style="text-align: center;">
                 <h2 style="font-size: 40px; font-weight: 900; margin-bottom: 80px;">{label}</h2>
                 <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 40px; position:relative;">
                     <div style="position: absolute; top: 32px; left: 15%; right: 15%; height: 2px; background: rgba(255,255,255,0.1); border-top: 2px dashed rgba(255,255,255,0.2); z-index: 1;"></div>
                     {steps_html}
                 </div>
             </div>
             '''
        elif ctype == "bento_grid":
             return f'''
             <div class="col-span-12 section-padding">
                <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 32px; min-height: 500px;">
                    <div class="card-premium" style="display: flex; flex-direction: column; justify-content: center; background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(139, 92, 246, 0.1) 100%);">
                        <h2 style="font-size: 40px; font-weight: 900; marginBottom: 24px;">{label}</h2>
                        <p style="font-size: 18px; opacity: 0.7; marginBottom: 40px; max-width: 90%;">{content}</p>
                        <div>
                             <a href="#" class="btn btn-primary">{subtext or "Learn More"}</a>
                        </div>
                        <div style="margin-top: auto; height: 200px; background: rgba(0,0,0,0.2); border-radius: 16px; margin-top: 40px;"></div>
                    </div>
                    <div style="display: grid; gap: 32px;">
                        <div class="card-premium" style="background: #0F172A;">
                             <div style="font-size:32px; margin-bottom:16px;">🚀</div>
                             <h3 style="font-weight:800; font-size:24px;">High Performance</h3>
                        </div>
                        <div class="card-premium" style="background: var(--primary);">
                             <div style="font-size:32px; margin-bottom:16px; color: white;">🛡️</div>
                             <h3 style="font-weight:800; font-size:24px; color: white;">Secure & Private</h3>
                        </div>
                    </div>
                </div>
             </div>
             '''
        elif ctype == "mobile_showcase":
             return f'''
             <div class="col-span-12 section-padding">
                 <div class="hero-split">
                     <div>
                         <h2 style="font-size: 48px; font-weight: 900; margin-bottom: 32px;">{label}</h2>
                         <ul style="list-style:none; display:flex; flex-direction:column; gap: 24px; margin-bottom: 48px;">
                            <li style="display:flex; gap:16px; align-items:center;">
                                <div style="width:24px; height:24px; background:var(--primary); border-radius:50%; display:flex;align-items:center;justify-content:center;font-size:12px;">✓</div>
                                <span style="font-size:18px; font-weight:600;">Always connected, wherever you go</span>
                            </li>
                            <li style="display:flex; gap:16px; align-items:center;">
                                <div style="width:24px; height:24px; background:var(--primary); border-radius:50%; display:flex;align-items:center;justify-content:center;font-size:12px;">✓</div>
                                <span style="font-size:18px; font-weight:600;">Real-time notifications & alerts</span>
                            </li>
                            <li style="display:flex; gap:16px; align-items:center;">
                                <div style="width:24px; height:24px; background:var(--primary); border-radius:50%; display:flex;align-items:center;justify-content:center;font-size:12px;">✓</div>
                                <span style="font-size:18px; font-weight:600;">Seamless cross-device sync</span>
                            </li>
                         </ul>
                         <button class="btn btn-primary">Download App</button>
                     </div>
                     <div style="display:flex; justify-content:center; position:relative;">
                        <div class="mockup-phone" style="width: 300px; height: 600px; position: relative; z-index: 2;">
                            <div style="width:100%; height:100%; background: var(--surface); display:flex; flex-direction:column;">
                                <div style="height:60px; border-bottom:1px solid rgba(255,255,255,0.1); display:flex; align-items:center; justify-content:center; font-weight:800;">{label}</div>
                                <div style="padding: 20px;">
                                    <div style="background:rgba(255,255,255,0.05); height:120px; border-radius:12px; margin-bottom:12px;"></div>
                                    <div style="background:rgba(255,255,255,0.05); height:60px; border-radius:12px; margin-bottom:12px;"></div>
                                    <div style="background:rgba(255,255,255,0.05); height:60px; border-radius:12px; margin-bottom:12px;"></div>
                                </div>
                            </div>
                        </div>
                        <div style="position:absolute; inset: -20px; background: var(--gradient-primary); filter: blur(60px); opacity: 0.4; z-index: 1;"></div>
                     </div>
                 </div>
             </div>
             '''
        elif ctype == "herosplit":
            return f'''
            <div class="col-span-12 hero-split">
                <div>
                    <h2 style="font-size: 56px; font-weight: 900; margin-bottom: 24px; letter-spacing: -0.03em;">{label}</h2>
                    <p style="font-size: 18px; opacity: 0.7; margin-bottom: 40px;">{content}</p>
                    <a href="{link_url}" class="btn btn-primary">{subtext or "Get Started"}</a>
                </div>
                <div class="card-premium glass" style="height: 500px; display: flex; align-items: center; justify-content: center; font-size: 14px; opacity: 0.4;">
                    [Interactive Visualization: {label}]
                </div>
            </div>
            '''
        elif ctype == "authcard":
             is_reg = "register" in label.lower() or "up" in label.lower()
             return f'''
             <div style="width: 100%; display: flex; justify-content: center; align-items: center; padding: 40px 0;">
                 <div class="card-premium glass" style="width: 480px; padding: 56px; margin: 0 auto; box-shadow: 0 40px 100px -20px rgba(0,0,0,0.6); position: relative; z-index: 10;">
                <div style="text-align: center; margin-bottom: 48px;">
                    <div class="logo-icon" style="margin: 0 auto 24px;"></div>
                    <h2 style="font-size: 32px; font-weight: 900; margin-bottom: 8px; letter-spacing: -0.04em;">{label}</h2>
                    <p style="opacity: 0.6; font-size: 15px;">Secure access to your professional workspace</p>
                </div>
                
                <div style="margin-bottom: 24px;">
                    <label style="display:block; font-size:11px; font-weight:800; margin-bottom:10px; opacity:0.5; text-transform:uppercase; letter-spacing:1px;">EMAIL ADDRESS</label>
                    <input type="email" class="input-field" placeholder="name@domain.com" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); padding: 18px 24px;">
                </div>
                <div style="margin-bottom: 40px;">
                    <label style="display:block; font-size:11px; font-weight:800; margin-bottom:10px; opacity:0.5; text-transform:uppercase; letter-spacing:1px;">PASSWORD</label>
                    <input type="password" class="input-field" placeholder="••••••••" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); padding: 18px 24px;">
                </div>
                
                <button class="btn btn-primary" style="width:100%; padding: 18px; font-size: 16px; margin-bottom: 32px;">{label}</button>
                <p style="font-size: 14px; text-align: center; opacity: 0.6;">
                    { 'Already have an account? <a href="login.html" style="color:var(--primary); font-weight:700; text-decoration:none;">Sign In</a>' if is_reg else 'New here? <a href="register.html" style="color:var(--primary); font-weight:700; text-decoration:none;">Create Account</a>' }
                </p>
             </div>
             </div>
             '''
        elif ctype == "cartitem":
            return f'''
            <div class="col-span-12 card-premium glass" style="display: flex; gap: 24px; align-items: center; margin-bottom: 12px; padding: 20px;">
                <div style="width: 80px; height: 80px; background: rgba(255,255,255,0.05); border-radius: 12px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; font-size: 24px;">📦</div>
                <div style="flex: 1;">
                    <h4 style="font-weight: 800; font-size: 18px; margin-bottom: 4px;">{label}</h4>
                    <p style="opacity: 0.6; font-size: 14px;">{subtext}</p>
                </div>
                <div style="text-align: right;">
                    <div style="font-weight: 900; font-size: 18px; color: var(--primary);">{content}</div>
                    <div style="font-size: 12px; opacity: 0.4; text-decoration: underline; margin-top: 8px; cursor: pointer;">Remove</div>
                </div>
            </div>
            '''
        elif ctype == "summary":
            return f'''
            <div class="col-span-12 card-premium" style="background: rgba(255,255,255,0.02);">
                <h3 style="font-weight: 800; margin-bottom: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 16px;">{label}</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; opacity: 0.7;">
                    <span>Subtotal</span>
                    <span>{content}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; opacity: 0.7;">
                    <span>Shipping</span>
                    <span>$12.00</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 12px; opacity: 0.7;">
                    <span>Tax</span>
                    <span>$8.40</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border-color); font-weight: 900; font-size: 20px;">
                    <span>Total</span>
                    <span style="color: var(--primary);">$148.40</span>
                </div>
                <button class="btn btn-primary" style="width: 100%; margin-top: 32px;">Complete Purchase</button>
            </div>
            '''
        elif ctype == "form":
            return f'''
            <div class="col-span-12 card-premium">
                <h3 style="font-weight: 800; margin-bottom: 24px;">{label}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div style="grid-column: span 2;">
                        <label style="display:block; font-size:12px; font-weight:700; margin-bottom:8px; opacity:0.6;">FULL NAME</label>
                        <input type="text" class="input-field" placeholder="John Doe">
                    </div>
                    <div>
                        <label style="display:block; font-size:12px; font-weight:700; margin-bottom:8px; opacity:0.6;">EMAIL</label>
                        <input type="email" class="input-field" placeholder="john@example.com">
                    </div>
                    <div>
                        <label style="display:block; font-size:12px; font-weight:700; margin-bottom:8px; opacity:0.6;">PHONE</label>
                        <input type="tel" class="input-field" placeholder="+1 (555) 000-0000">
                    </div>
                    <div style="grid-column: span 2;">
                        <label style="display:block; font-size:12px; font-weight:700; margin-bottom:8px; opacity:0.6;">SHIPPING ADDRESS</label>
                        <textarea class="input-field" style="height: 80px; resize: none;" placeholder="123 Luxury St, Beverly Hills, CA"></textarea>
                    </div>
                </div>
            </div>
            '''
        elif ctype == "projectcard" or ctype == "card":
            span = comp.get("span", 4)
            return f'''
            <div class="col-span-{span} card-premium">
               <div style="aspect-ratio: 16/10; background: rgba(255,255,255,0.03); border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; font-size: 32px;">🖼️</div>
               <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
                   <h3 style="font-weight: 800; font-size: 18px;">{label}</h3>
                   {f'<span style="color: var(--primary); font-weight: 900;">{subtext}</span>' if '$' in subtext else ''}
               </div>
               <p style="opacity:0.6; font-size:14px; line-height:1.6; margin-bottom: 20px;">{content}</p>
               {f'<div class="btn btn-outline" style="width: 100%;">{subtext if "$" not in subtext else "View Details"}</div>' if subtext else ''}
            </div>
            '''
        elif ctype == "statcard" or (ctype == "stats_grid" and not isinstance(parsed_data, list)):
            span = comp.get("span", 4)
            val = content if not parsed_data else str(parsed_data)
            return f'''
            <div class="col-span-{span}">
                <div class="card-premium glass">
                    <h4 style="font-size: 12px; font-weight: 800; opacity: 0.5; text-transform: uppercase; margin-bottom: 12px;">{label}</h4>
                    <div style="font-size: 32px; font-weight: 900; margin-bottom: 8px; color: var(--primary);">{val}</div>
                    <p style="font-size: 13px; opacity: 0.6;">{subtext}</p>
                </div>
            </div>
            '''
        elif ctype == "stats_grid" and isinstance(parsed_data, list):
            items_html = ""
            for item in parsed_data:
                item_label = item.get("label", item.get("name", "Metric"))
                item_val = item.get("value", item.get("count", "0"))
                items_html += f'''
                <div class="card-premium glass" style="padding: 24px;">
                    <h4 style="font-size: 11px; font-weight: 800; opacity: 0.5; text-transform: uppercase; margin-bottom: 8px;">{item_label}</h4>
                    <div style="font-size: 28px; font-weight: 900; color: var(--primary);">{item_val}</div>
                </div>
                '''
            return f'''
            <div class="col-span-12">
                <h3 style="margin-bottom: 24px; font-weight: 800;">{label}</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                    {items_html}
                </div>
            </div>
            '''
        elif ctype == "testimonials":
            items = parsed_data if isinstance(parsed_data, list) else []
            if not items and isinstance(sim_data, dict): items = sim_data.get("items", [])
            
            cards_html = ""
            for item in items:
                user = item.get("user", item.get("author", "Verified User"))
                quote = item.get("quote", item.get("content", item.get("text", "")))
                rating = "★" * int(item.get("rating", 5))
                cards_html += f'''
                <div class="card-premium glass" style="padding: 32px;">
                    <div style="color: #FBBF24; margin-bottom: 16px; letter-spacing: 2px;">{rating}</div>
                    <p style="font-style: italic; opacity: 0.8; margin-bottom: 24px; line-height: 1.7;">"{quote}"</p>
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="width: 32px; height: 32px; border-radius: 50%; background: var(--primary); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 900;">{user[0].upper()}</div>
                        <span style="font-weight: 700; font-size: 14px;">{user}</span>
                    </div>
                </div>
                '''
            return f'''
            <div class="col-span-12 section-padding">
                <h2 style="text-align: center; font-size: 32px; font-weight: 900; margin-bottom: 48px;">{label}</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 32px;">
                    {cards_html or '<p style="text-align:center; opacity:0.5;">[Client Testimonials Configuration]</p>'}
                </div>
            </div>
            '''
        elif ctype == "pricing":
            items = parsed_data if isinstance(parsed_data, list) else [
                {"name": "Starter", "price": "Free", "feat": ["Basic Analytics", "1 Project", "Email Support"]},
                {"name": "Pro", "price": "$29", "feat": ["Advanced AI", "Unlimited Projects", "Priority Support"]},
                {"name": "Elite", "price": "$99", "feat": ["Custom Models", "API Access", "Dedicated Manager"]}
            ]
            cards_html = ""
            for item in items:
                name = item.get("name", "Plan")
                price = item.get("price", "$0")
                feats = item.get("features", item.get("feat", []))
                feats_html = "".join([f'<li style="margin-bottom:12px; font-size:14px; opacity:0.7;">✓ {f}</li>' for f in feats])
                is_pro = "pro" in name.lower()
                border = "2px solid var(--primary)" if is_pro else "1px solid var(--border-color)"
                cards_html += f'''
                <div class="card-premium glass" style="border: {border}; display: flex; flex-direction: column;">
                    <h3 style="font-weight: 900; font-size: 20px; margin-bottom: 8px;">{name}</h3>
                    <div style="font-size: 40px; font-weight: 900; margin-bottom: 24px;">{price}<span style="font-size:14px; opacity:0.5;">/mo</span></div>
                    <ul style="list-style: none; margin-bottom: 32px; flex: 1;">
                        {feats_html}
                    </ul>
                    <button class="btn {'btn-primary' if is_pro else 'btn-outline'}" style="width: 100%;">Get Started</button>
                </div>
                '''
            return f'''
            <div class="col-span-12 section-padding">
                <h2 style="text-align: center; font-size: 32px; font-weight: 900; margin-bottom: 48px;">{label}</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 32px;">
                    {cards_html}
                </div>
            </div>
            '''
        elif ctype == "feed":
            items = parsed_data if isinstance(parsed_data, list) else []
            if not items: items = sim_data.get("items", [])
            if not items: items = [{"text": content, "author": "System", "time": "Just now"}]
            
            feed_html = ""
            for item in items:
                content_text = item.get("text", item.get("content", item)) if isinstance(item, dict) else item
                author = item.get("author", item.get("user", "Verified User")) if isinstance(item, dict) else "System"
                time = item.get("time", item.get("date", "2h ago")) if isinstance(item, dict) else "2h ago"
                feed_html += f'''
                <div class="card-premium glass" style="margin-bottom: 24px; padding: 28px;">
                    <div style="display: flex; gap: 16px; align-items: center; margin-bottom: 20px;">
                        <div style="width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, var(--primary), var(--accent)); display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 16px; color: white;">{str(author)[0].upper()}</div>
                        <div style="flex: 1;">
                            <div style="font-weight: 800; font-size: 15px;">{author}</div>
                            <div style="font-size: 12px; opacity: 0.5;">{time}</div>
                        </div>
                        <div style="opacity: 0.3; font-size: 18px;">•••</div>
                    </div>
                    <p style="font-size: 16px; line-height: 1.6; opacity: 0.9; margin-bottom: 20px;">{content_text}</p>
                    { '<div style="aspect-ratio: 16/9; background: rgba(0,0,0,0.2); border-radius: 12px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center; color: rgba(255,255,255,0.1); font-size: 14px;">[Media Content]</div>' if len(str(content_text)) > 100 else '' }
                    <div style="display: flex; gap: 32px; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 20px; opacity: 0.6; font-size: 13px; font-weight: 700;">
                        <span>❤️ {item.get("likes", 24) if isinstance(item, dict) else 12}</span>
                        <span>💬 {item.get("comments", 8) if isinstance(item, dict) else 4}</span>
                        <span>🔄 {item.get("shares", 3) if isinstance(item, dict) else 1}</span>
                    </div>
                </div>
                '''
            return f'''
            <div class="col-span-12" style="max-width: 800px; margin: 0 auto;">
                <h3 style="margin-bottom: 32px; font-weight: 800; font-size: 24px;">{label}</h3>
                {feed_html}
            </div>
            '''
        elif ctype == "profileheader":
            # (Profile header logic remains similar but with better defaults/fallback)
            stats = sim_data.get("stats", [{"label": "Followers", "value": "2.4k"}, {"label": "Following", "value": "842"}])
            stats_html = "".join([f'<div style="text-align:center;"><div style="font-weight:900; font-size:24px; color:var(--primary);">{s["value"]}</div><div style="font-size:11px; opacity:0.5; text-transform:uppercase; letter-spacing:1px;">{s["label"]}</div></div>' for s in stats])
            return f'''
            <div class="col-span-12 card-premium glass" style="padding: 0; overflow: hidden; margin-bottom: 40px; border-radius: 32px;">
                <div style="height: 220px; background: linear-gradient(135deg, var(--bg-color), var(--primary), var(--accent)); opacity: 0.4;"></div>
                <div style="padding: 0 48px 40px; margin-top: -80px; display: flex; align-items: flex-end; gap: 40px; flex-wrap: wrap;">
                    <div style="width: 160px; height: 160px; border-radius: 40px; background: var(--surface); border: 8px solid var(--bg-color); display: flex; align-items: center; justify-content: center; font-size: 64px; box-shadow: var(--shadow-premium); position: relative; z-index: 10;">👤</div>
                    <div style="flex: 1; min-width: 300px; padding-bottom: 8px;">
                        <h2 style="font-size: 38px; font-weight: 900; margin-bottom: 8px; letter-spacing: -0.02em;">{label}</h2>
                        <p style="opacity: 0.6; font-size: 18px; max-width: 600px;">{content}</p>
                    </div>
                    <div style="display: flex; gap: 48px; padding-bottom: 12px; background: rgba(0,0,0,0.2); padding: 20px 40px; border-radius: 20px; backdrop-filter: blur(10px);">
                        {stats_html}
                    </div>
                </div>
            </div>
            '''
        elif ctype == "standalone_button":
             return f'''
             <div class="col-span-12" style="display:flex; justify-content:flex-start; margin-top: 12px; margin-bottom: 24px;">
                <button class="btn btn-primary" style="padding: 18px 48px; font-size: 16px; min-width: 240px;">{label}</button>
             </div>
             '''
        elif ctype == "field_box":
             placeholder = content or f"Enter {label}..."
             return f'''
             <div class="col-span-12" style="margin-bottom: 24px;">
                <label style="display:block; font-size:12px; font-weight:800; margin-bottom:10px; opacity:0.5; text-transform:uppercase; letter-spacing:1px;">{label}</label>
                <input type="text" class="input-field" placeholder="{placeholder}" style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-color); padding: 18px 24px;">
             </div>
             '''
        elif ctype == "features":
             items = parsed_data if isinstance(parsed_data, list) else sim_data.get("items", [])
             if not items:
                 # Generate rich default items if none exist
                 items = [
                     {"title": "Advanced Analytics", "desc": "Gain deep insights into your performance metrics with our real-time tracking engine. Understand behavior like never before."},
                     {"title": "Global Reach", "desc": "Connect with audiences worldwide through our low-latency distributed network. No boundaries, just connection."},
                     {"title": "Secure Encryption", "desc": "Your data is protected by military-grade AES-256 encryption. We prioritize your privacy above all else."}
                 ]
             
             cards_html = ""
             for item in items:
                 i_title = item.get("title", "Feature") if isinstance(item, dict) else str(item)
                 i_desc = item.get("desc", item.get("description", "Experience the power of our platform with this cutting-edge feature designed for growth.")) if isinstance(item, dict) else "Detailed feature description goes here."
                 
                 cards_html += f'''
                 <div class="card-premium glass" style="padding: 40px;">
                     <div style="width: 48px; height: 48px; background: rgba(255,255,255,0.05); border-radius: 12px; margin-bottom: 24px; display:flex; align-items:center; justify-content:center; font-size:24px;">⚡</div>
                     <h3 style="font-size: 22px; font-weight: 800; margin-bottom: 16px;">{i_title}</h3>
                     <p style="opacity: 0.7; font-size: 16px; line-height: 1.7;">{i_desc}</p>
                 </div>
                 '''
             return f'''
             <div class="col-span-12 section-padding">
                 <h2 style="font-size: 48px; font-weight: 900; text-align: center; margin-bottom: 64px;">{label}</h2>
                 <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 32px;">
                     {cards_html}
                 </div>
             </div>
             '''
        elif ctype == "table":
            rows = sim_data.get("rows", parsed_data if isinstance(parsed_data, list) else [])
            rows_html = ""
            for row in rows:
                if isinstance(row, dict):
                    name_val = row.get("name", row.get("title", row.get("user", "Unknown")))
                    meta_val = row.get("status", row.get("value", row.get("role", "N/A")))
                    action_val = row.get("action", "Manage")
                else:
                    name_val = row
                    meta_val = "Active"
                    action_val = "View"
                
                rows_html += f'''
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); transition: background 0.2s;" onmouseover="this.style.background='rgba(255,255,255,0.02)'" onmouseout="this.style.background='transparent'">
                    <td style="padding: 20px 24px; font-weight: 700;">{name_val}</td>
                    <td style="padding: 20px 24px;"><span style="background: rgba(139, 92, 246, 0.1); color: var(--primary); padding: 4px 12px; border-radius: 99px; font-size: 12px; font-weight: 800;">{meta_val}</span></td>
                    <td style="padding: 20px 24px; text-align: right;"><span class="btn btn-outline" style="padding: 8px 16px; font-size: 12px;">{action_val}</span></td>
                </tr>
                '''
            
            return f'''
            <div class="col-span-12">
                <div class="card-premium glass" style="padding: 0; border-radius: 24px; overflow: hidden;">
                    <div style="padding: 28px 32px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02);">
                        <h3 style="font-weight: 900; font-size: 20px;">{label}</h3>
                        <div class="btn btn-primary" style="padding: 10px 20px; font-size: 12px;">Export Data</div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="opacity: 0.4; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; background: rgba(0,0,0,0.1);">
                            <th style="text-align: left; padding: 16px 24px;">Primary Entity</th>
                            <th style="text-align: left; padding: 16px 24px;">Status/Value</th>
                            <th style="text-align: right; padding: 16px 24px;">Quick Action</th>
                        </tr>
                        {rows_html if rows_html else '<tr><td colspan="3" style="padding: 60px; text-align: center; opacity: 0.3;">No records found matching criteria</td></tr>'}
                    </table>
                </div>
            </div>
            '''
        else:
            return f'''<div class="col-span-12 card-premium glass" style="padding: 40px;">
                <h3 style="margin-bottom: 16px; font-weight: 800; color: var(--primary);">{label}</h3>
                <p style="opacity:0.75; font-size: 16px; line-height: 1.7;">{content}</p>
            </div>'''

    def generate_index(self, screens: List[Dict[str, Any]]) -> str:
        links_html = "".join([f'<li><a href="{s["url"]}">{s["name"]}</a></li>' for s in screens])
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>UI Design Navigation</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet">
</head>
<body style="display:flex; align-items:center; justify-content:center; min-height:100vh;">
    <div class="card-premium glass" style="width: 500px; text-align: center;">
        <h1 style="font-size: 32px; font-weight: 900; margin-bottom: 12px;">Project Screens</h1>
        <p style="opacity: 0.6; margin-bottom: 40px;">Select a screen to preview the high-fidelity UI design.</p>
        <ul style="list-style: none; text-align: left; display: flex; flex-direction: column; gap: 12px;">
            {links_html}
        </ul>
    </div>
</body>
</html>
"""
