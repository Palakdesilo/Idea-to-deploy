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

    def render_project(self, project_id: str, wireframes: List[Dict[str, Any]], ui_design: Dict[str, Any], project_name: str = "Project"):
        from .project_manager import ARTIFACTS_DIR
        output_dir = ARTIFACTS_DIR / project_id / "ui"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tokens = ui_design.get("design_tokens", self.default_tokens)
        palette = tokens.get("palette", tokens.get("colors", self.default_tokens["palette"]))
        
        # Premium CSS with Glassmorphism and HSL
        css = f"""
:root {{
    --primary: {palette.get('primary', '#8B5CF6')};
    --bg-color: {palette.get('background', '#0F172A')};
    --surface: {palette.get('surface', palette.get('card_bg', '#1E293B'))};
    --accent: {palette.get('accent', '#F472B6')};
    --text-primary: {palette.get('foreground', palette.get('text_main', '#F8FAFC'))};
    --text-secondary: #94A3B8;
    --border-color: rgba(255, 255, 255, 0.1);
    --radius-lg: 24px;
    --radius-md: 16px;
    --shadow-premium: 0 20px 40px -10px rgba(0,0,0,0.5);
    --font-family: 'Outfit', 'Inter', sans-serif;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background-color: var(--bg-color); font-family: var(--font-family); color: var(--text-primary); line-height: 1.6; }}
.ui-container {{ max-width: 1400px; margin: 0 auto; }}
.glass {{ background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(20px); border: 1px solid var(--border-color); }}
.screen-card {{ min-height: 100vh; display: flex; flex-direction: column; overflow: hidden; position: relative; }}

header {{ display: flex; justify-content: space-between; align-items: center; padding: 20px 40px; position: sticky; top: 0; z-index: 100; border-bottom: 1px solid var(--border-color); background: rgba(15, 23, 42, 0.8); backdrop-filter: blur(10px); }}
.logo {{ font-size: 22px; font-weight: 900; letter-spacing: -0.02em; display: flex; align-items: center; gap: 10px; }}
.logo-icon {{ width: 32px; height: 32px; background: linear-gradient(135deg, var(--primary), var(--accent)); border-radius: 8px; }}

.nav-links {{ display: flex; gap: 24px; align-items: center; }}
.nav-links a {{ text-decoration: none; color: var(--text-primary); font-weight: 500; font-size: 14px; transition: color 0.2s; opacity: 0.8; }}
.nav-links a:hover {{ opacity: 1; color: var(--primary); }}

.section-padding {{ padding: 100px 40px; }}
.hero-split {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 80px; align-items: center; padding: 120px 40px; }}

.grid-layout {{ display: grid; gap: 24px; }}
.grid-cols-12 {{ grid-template-columns: repeat(12, 1fr); }}
.col-span-12 {{ grid-column: span 12; }}
.col-span-8 {{ grid-column: span 8; }}
.col-span-6 {{ grid-column: span 6; }}
.col-span-4 {{ grid-column: span 4; }}
.col-span-3 {{ grid-column: span 3; }}

.card-premium {{ background: var(--surface); border-radius: var(--radius-md); padding: 32px; border: 1px solid var(--border-color); transition: transform 0.3s; position: relative; overflow: hidden; }}
.card-premium:hover {{ transform: translateY(-5px); box-shadow: var(--shadow-premium); }}

.btn {{ padding: 12px 28px; border-radius: 99px; font-weight: 700; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; transition: all 0.2s; cursor: pointer; border: none; font-size: 14px; }}
.btn-primary {{ background: linear-gradient(135deg, var(--primary), var(--accent)); color: white; }}
.btn-outline {{ background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); }}
.btn-outline:hover {{ background: rgba(255, 255, 255, 0.05); }}

.input-field {{ background: rgba(0,0,0,0.2); border: 1px solid var(--border-color); border-radius: 12px; padding: 14px 18px; color: white; width: 100%; outline: none; }}
.input-field:focus {{ border-color: var(--primary); }}

footer {{ padding: 80px 40px; border-top: 1px solid var(--border-color); margin-top: auto; opacity: 0.8; }}
.footer-grid {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }}

/* App Layout Styles */
.app-shell {{ display: flex; height: 100vh; overflow: hidden; }}
.sidebar {{ width: 280px; background: rgba(0,0,0,0.2); border-right: 1px solid var(--border-color); padding: 32px; display: flex; flex-direction: column; flex-shrink: 0; }}
.app-main {{ flex: 1; overflow-y: auto; background: var(--bg-color); }}
.top-bar {{ height: 80px; padding: 0 40px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; }}

.avatar {{ width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--accent)); display: flex; align-items: center; justify-content: center; font-weight: 800; }}
"""
        with open(output_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(css)

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
            cols = section.get("grid_cols", 12)
            
            section_content = ""
            for comp in section.get("components", []):
                section_content += self._render_component(comp, is_app, nav_map)
            
            if layout_type == "heroSplit":
                content_html += f'<div class="hero-split">{section_content}</div>'
            elif layout_type == "masonryGrid":
                 content_html += f'<div class="grid-layout grid-cols-12 section-padding" style="gap: 20px;">{section_content}</div>'
            elif layout_type == "authShell":
                 content_html += f'<div style="display:flex; align-items:center; justify-content:center; min-height:80vh; padding:40px;">{section_content}</div>'
            else:
                content_html += f'<div class="grid-layout grid-cols-12 section-padding">{section_content}</div>'

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
<body>
    <div class="app-shell">
        <aside class="sidebar">
            <div class="logo">
                <div class="logo-icon"></div>
                {project_name[:12].upper()}
            </div>
            <nav class="sidebar-menu" style="margin-top: 40px; display:flex; flex-direction:column; gap:8px;">
                {sidebar_menu}
            </nav>
            <div style="margin-top: auto;" class="avatar">U</div>
        </aside>
        <main class="app-main">
            <header class="top-bar">
                <h1 style="font-size: 20px; font-weight: 800;">{screen_name}</h1>
                <div style="display: flex; gap: 20px; align-items:center;">
                    <div class="btn btn-outline" style="padding: 10px 20px; font-size:12px;">+ Create New</div>
                </div>
            </header>
            {content_html}
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
<body>
    <div class="screen-card">
        <header>
             <div class="logo">
                <div class="logo-icon"></div>
                {project_name.upper()}
             </div>
             <nav class="nav-links">
                {header_links}
                <div class="btn btn-primary">Get Started</div>
            </nav>
        </header>
        {content_html}
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
        ctype = comp.get("type", "Box").lower()
        label = comp.get("label", "Component")
        content = comp.get("content", "")
        subtext = comp.get("subtext", "")
        
        # Link mapping
        link_url = "#"
        if label.lower() in nav_map: link_url = nav_map[label.lower()]

        if ctype == "hero":
            return f'''
            <div class="col-span-12" style="text-align: center; padding: 60px 0;">
                <h1 style="font-size: 72px; font-weight: 900; margin-bottom: 24px; line-height: 1.1; letter-spacing: -0.04em;">{label}</h1>
                <p style="font-size: 20px; opacity: 0.6; max-width: 800px; margin: 0 auto 48px;">{content}</p>
                <div style="display: flex; gap: 16px; justify-content: center;">
                    <a href="{link_url}" class="btn btn-primary">{subtext or "Get Started"}</a>
                    <div class="btn btn-outline">Learn More</div>
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
             <div class="card-premium glass" style="width: 440px; padding: 48px;">
                <h2 style="font-size: 28px; font-weight: 800; margin-bottom: 8px; text-align: center;">{label}</h2>
                <p style="opacity: 0.6; font-size: 14px; margin-bottom: 40px; text-align: center;">Secure access to your workspace</p>
                
                <div style="margin-bottom: 20px;">
                    <label style="display:block; font-size:12px; font-weight:700; margin-bottom:8px; opacity:0.8;">EMAIL ADDRESS</label>
                    <input type="email" class="input-field" placeholder="name@domain.com">
                </div>
                <div style="margin-bottom: 32px;">
                    <label style="display:block; font-size:12px; font-weight:700; margin-bottom:8px; opacity:0.8;">PASSWORD</label>
                    <input type="password" class="input-field" placeholder="••••••••">
                </div>
                
                <button class="btn btn-primary" style="width:100%; margin-bottom: 24px;">{label}</button>
                <p style="font-size: 13px; text-align: center; opacity: 0.6;">
                    { 'Already have an account? <a href="login.html" style="color:var(--primary); font-weight:700;">Sign In</a>' if is_reg else 'New here? <a href="register.html" style="color:var(--primary); font-weight:700;">Create Account</a>' }
                </p>
             </div>
             '''
        elif ctype == "statcard" or ctype == "card":
            span = comp.get("span", 4)
            return f'''
            <div class="col-span-{span}">
                <div class="card-premium">
                    <h4 style="font-size: 12px; font-weight: 800; opacity: 0.5; text-transform: uppercase; margin-bottom: 12px;">{label}</h4>
                    <div style="font-size: 32px; font-weight: 900; margin-bottom: 8px;">{content or "[Value]"}</div>
                    <p style="font-size: 13px; opacity: 0.6;">{subtext}</p>
                </div>
            </div>
            '''
        elif ctype == "table":
            return f'''
            <div class="col-span-12">
                <div class="card-premium" style="padding: 0;">
                    <div style="padding: 24px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between;">
                        <h3 style="font-weight: 800;">{label}</h3>
                        <div class="btn btn-outline" style="padding: 6px 12px; font-size: 11px;">View All</div>
                    </div>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="opacity: 0.5; font-size: 11px; text-transform: uppercase;">
                            <th style="text-align: left; padding: 16px 24px;">Entry</th>
                            <th style="text-align: left; padding: 16px 24px;">Metadata</th>
                            <th style="text-align: right; padding: 16px 24px;">Action</th>
                        </tr>
                        <tr>
                            <td style="padding: 16px 24px; font-weight: 600;">Sample Entry</td>
                            <td style="padding: 16px 24px; opacity: 0.6;">Value data point</td>
                            <td style="padding: 16px 24px; text-align: right;"><span class="btn btn-outline" style="padding: 4px 10px; font-size: 10px;">Select</span></td>
                        </tr>
                    </table>
                </div>
            </div>
            '''
        elif ctype == "featuregrid":
             return f'''
             <div class="col-span-4 card-premium">
                <div style="width:48px; height:48px; background:rgba(255,255,255,0.05); border-radius:12px; margin-bottom:24px; display:flex; align-items:center; justify-content:center; font-size:20px;">✨</div>
                <h3 style="font-weight: 800; margin-bottom: 12px;">{label}</h3>
                <p style="opacity:0.6; font-size:14px; line-height:1.6;">{content}</p>
             </div>
             '''
        else:
            return f'''<div class="col-span-12 card-premium"><h3>{label}</h3><p style="opacity:0.6;">{content}</p></div>'''

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
