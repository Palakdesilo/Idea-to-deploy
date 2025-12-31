import json
from pathlib import Path
from typing import Dict, List, Any

class WireframeRenderer:
    def __init__(self):
        # Precise Design System from wireframe_prototype/low-fi-system.css
        self.css_content = """
:root {
    --bg-color: #f5f5f5;
    --card-bg: #ffffff;
    --border-color: #e0e0e0;
    --text-primary: #1a1a1a;
    --text-secondary: #757575;
    --placeholder-bg: #f9f9f9;
    --primary-btn: #121212;
    --primary-btn-text: #ffffff;
    --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background-color: var(--bg-color);
    font-family: var(--font-family);
    color: var(--text-primary);
    padding: 40px;
    line-height: 1.5;
}

.wireframe-container {
    max-width: 1200px;
    margin: 0 auto;
}

.screen-card {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 32px;
    margin-bottom: 40px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    position: relative;
}

header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 24px;
}

.screen-info h1 { font-size: 20px; font-weight: 600; }
.screen-info p { font-size: 14px; color: var(--text-secondary); }

.nav-links { display: flex; gap: 12px; }

.placeholder-box {
    background: var(--placeholder-bg);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    padding: 12px;
    color: var(--text-secondary);
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 40px;
}

.grid { display: grid; gap: 20px; }
.grid-2 { grid-template-columns: 1fr 1fr; }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

.section { margin-top: 32px; }
.section-title { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 12px; }

.btn {
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    border: 1px solid var(--border-color);
    background: var(--card-bg);
    color: var(--text-primary);
    text-align: center;
    display: inline-block;
    width: fit-content;
}

.btn-primary {
    background: var(--primary-btn);
    color: var(--primary-btn-text);
    border: none;
}

.input-field {
    width: 100%;
    padding: 12px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    background: var(--placeholder-bg);
    color: var(--text-secondary);
    font-size: 14px;
    margin-bottom: 16px;
}

.sidebar {
    width: 200px;
    border-right: 1px solid var(--border-color);
    padding-right: 20px;
    flex-shrink: 0;
}

.flex { display: flex; gap: 20px; }
.col { display: flex; flex-direction: column; gap: 8px; }
.flex-1 { flex: 1; }

.annotation { font-size: 12px; color: var(--text-secondary); margin-top: 12px; }
.status-labels { font-size: 12px; color: var(--text-secondary); text-align: right; }

.auth-card-container { width: 400px; padding: 32px; border: 1px solid var(--border-color); border-radius: 8px; background: white; }
.separator { text-align: center; border-bottom: 1px solid var(--border-color); line-height: 0.1em; margin: 10px 0 20px; }
.separator span { background:#fff; padding:0 10px; font-size: 12px; color: var(--text-secondary); }

table { width: 100%; border-collapse: collapse; font-size: 12px; }
th { border-bottom: 1px solid var(--border-color); text-align: left; padding: 10px; color: var(--text-secondary); }
td { border-bottom: 1px solid var(--border-color); padding: 10px; }
"""

    def render_project(self, project_id: str, wireframes_json: List[Dict[str, Any]]):
        from .project_manager import ARTIFACTS_DIR
        output_dir = ARTIFACTS_DIR / project_id / "wireframes"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(self.css_content)
            
        screens = []
        for wf in wireframes_json:
            html = self.generate_html(wf, wireframes_json)
            filename = f"{wf.get('screenKey', 'screen')}.html"
            with open(output_dir / filename, "w", encoding="utf-8") as f:
                f.write(html)
            screens.append({
                "name": wf.get("screen"),
                "key": wf.get("screenKey"),
                "url": filename
            })
            
        index_html = self.generate_index(screens)
        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

    def generate_html(self, wf: Dict[str, Any], all_screens: List[Dict[str, Any]]) -> str:
        # Create navigation map
        nav_map = { s.get("screen", "").lower(): f"{s.get('screenKey')}.html" for s in all_screens if s.get("screenKey") }
        nav_map.update({ s.get("screenKey", "").lower(): f"{s.get('screenKey')}.html" for s in all_screens if s.get("screenKey") })

        sidebar_html = ""
        footer_html = ""
        header_nav_html = ""
        main_content_html = ""
        
        # Cross-page navigation simulation
        top_nav_links = ""
        for s in all_screens[:5]:
            active_class = "btn-primary" if s.get("screenKey") == wf.get("screenKey") else ""
            top_nav_links += f'<a href="{s.get("screenKey")}.html" class="btn {active_class}" style="text-decoration:none;">{s.get("screen")}</a>'

        is_dashboard = any(x in wf.get("screen", "") for x in ["Dashboard", "Feed", "Home", "Analytics"])

        for section in wf.get("layout", []):
            s_type = section.get("section", "Main")
            section_html = ""
            
            for comp in section.get("components", []):
                ctype = comp.get("type", "Box")
                label = comp.get("label", "Label")
                content = comp.get("content", "Lorem ipsum...")
                subtext = comp.get("subtext", "")
                annot = comp.get("annotation", "")
                
                # Determine Link URL
                link_url = "#"
                if label.lower() in nav_map: link_url = nav_map[label.lower()]
                
                if ctype == "ProfileCircle":
                    header_nav_html += f'<a href="profile.html"><div class="placeholder-box" style="width:36px; height:36px; border-radius:50%;" title="{label}"></div></a>'
                elif ctype == "SearchBar":
                    header_nav_html += f'<div class="col" style="width:200px;"><div class="placeholder-box" style="height:34px; min-height:34px;">[Search Bar]</div></div>'
                elif ctype == "Link" and s_type == "Header":
                    header_nav_html += f'<a href="{link_url}" class="btn" style="text-decoration:none;">{label}</a>'
                elif ctype == "Button" and s_type == "Header":
                    header_nav_html += f'<a href="{link_url}" class="btn btn-primary" style="text-decoration:none;">{label}</a>'
                elif ctype == "Button" and s_type == "Sidebar":
                    active_style = "background:var(--border-color);" if s.get("screenKey") == wf.get("screenKey") else ""
                    sidebar_html += f'<a href="{link_url}" class="btn" style="text-align:left; text-decoration:none; {active_style}">{label}</a>'
                elif ctype == "Hero":
                    section_html += f'''
                        <div class="col" style="padding: 60px 0; text-align: center; border-bottom: 2px dashed var(--border-color); margin-bottom: 40px;">
                            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: 12px;">{label} [HERO]</h1>
                            <div class="placeholder-box" style="height: 60px; max-width: 600px; margin: 0 auto 24px;">{content[:100]}...</div>
                            <div class="flex" style="justify-content: center;">
                                <a href="{link_url}" class="btn btn-primary" style="text-decoration:none;">Primary CTA</a>
                                <div class="btn">Secondary Action</div>
                            </div>
                        </div>
                    '''
                elif ctype == "Image":
                    section_html += f'''
                        <div class="col" style="margin: 24px 0;">
                            <div class="placeholder-box" style="height: 300px; width: 100%; flex-direction: column;">
                                <div style="font-weight: bold; margin-bottom: 8px;">[IMAGE: {label}]</div>
                                <div style="font-size: 11px;">{subtext or "Asset Placeholder"}</div>
                            </div>
                        </div>
                    '''
                elif ctype == "StatCard":
                    section_html += f'''
                        <div class="col" style="border: 1px solid var(--border-color); padding: 16px; border-radius: 8px;">
                            <div class="section-title">{label}</div>
                            <div class="placeholder-box" style="height: 60px; font-size: 20px;">{content or "[Value]"}</div>
                            <p class="annotation">{subtext or annot or "Stat trend"}</p>
                        </div>
                    '''
                elif ctype == "PostCard":
                    section_html += f'''
                        <div class="col" style="border: 1px solid var(--border-color); padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                            <div class="flex" style="margin-bottom: 16px;">
                                <div class="placeholder-box" style="width: 40px; height: 40px; border-radius: 50%;"></div>
                                <div class="col flex-1">
                                    <div class="placeholder-box" style="height: 12px; width: 140px; margin-bottom: 6px;"></div>
                                    <div class="placeholder-box" style="height: 10px; width: 80px;"></div>
                                </div>
                            </div>
                            <div class="section-title">{label}</div>
                            <div class="placeholder-box" style="height: 80px; margin-bottom: 16px;">[Copy: {content[:50]}...]</div>
                            <div class="flex">
                                <div class="btn" style="font-size:11px;">[Action]</div>
                                <div class="btn btn-primary" style="font-size:11px;">[Primary]</div>
                            </div>
                        </div>
                    '''
                elif ctype == "Table":
                    rows_html = ""
                    try:
                        data_list = json.loads(content) if content.strip().startswith('[') else []
                        if isinstance(data_list, list):
                            for item in data_list:
                                item_name = item.get("item", "Record")
                                status = item.get("status", "ACTIVE")
                                rows_html += f'<tr><td>{item_name}</td><td>[Type]</td><td>{status}</td><td><span style="text-decoration:underline;">View</span></td></tr>'
                    except: pass
                    
                    if not rows_html:
                        rows_html = '<tr><td>[Placeholder Row]</td><td>[Type]</td><td>[Status]</td><td><span style="text-decoration:underline;">View</span></td></tr>'

                    section_html += f'''
                        <div class="col">
                            <div class="section-title">{label}</div>
                            <table>
                                <thead>
                                    <tr><th>Item</th><th>Type</th><th>Status</th><th>Action</th></tr>
                                </thead>
                                <tbody>
                                    {rows_html}
                                </tbody>
                            </table>
                        </div>
                    '''
                elif ctype == "SplitSection":
                    section_html += f'''
                    <div class="section grid grid-2" style="align-items: center;">
                        <div class="placeholder-box" style="height: 300px;">[Visual: {label}]</div>
                        <div>
                            <h2 style="margin-bottom: 12px;">{label}</h2>
                            <p style="color: var(--text-secondary); margin-bottom: 16px;">{content}</p>
                            <a href="{link_url}" class="btn">{subtext}</a>
                        </div>
                    </div>'''

                elif ctype == "ProductGrid":
                    grid_html = ""
                    for i in range(4):
                        grid_html += f'<div class="placeholder-box" style="height: 200px;">Product {i+1}</div>'
                    section_html += f'''
                    <div class="section">
                        <h3 class="section-title">{label}</h3>
                        <div class="grid grid-4">{grid_html}</div>
                    </div>'''

                elif ctype == "TestimonialGrid":
                    grid_html = ""
                    for i in range(3):
                        grid_html += f'<div class="placeholder-box" style="height: 120px;">Testimonial {i+1}</div>'
                    section_html += f'''
                    <div class="section">
                        <h3 class="section-title">{label}</h3>
                        <div class="grid grid-3">{grid_html}</div>
                    </div>'''

                elif ctype == "Newsletter":
                    section_html += f'''
                    <div class="section" style="background: var(--placeholder-bg); padding: 40px; text-align: center;">
                        <h4>{label}</h4>
                        <p style="margin-bottom: 16px;">{content}</p>
                        <div style="display: flex; justify-content: center; gap: 8px;">
                            <div class="placeholder-box" style="width: 200px;">Email Input</div>
                            <div class="btn btn-primary">{subtext}</div>
                        </div>
                    </div>'''

                elif ctype == "StatGrid":
                    grid_html = ""
                    for i in range(3):
                        grid_html += f'<div style="text-align: center; border-right: 1px solid var(--border-color);"><p style="font-size: 24px;">99%</p><p style="font-size: 11px;">METRIC</p></div>'
                    section_html += f'''
                    <div class="section grid grid-3" style="padding: 24px 0; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color);">{grid_html}</div>'''
                
                elif ctype == "AuthCard":
                    is_reg = "Register" in label or "Sign Up" in label or "Register" in wf.get("screen", "")
                    confirm_field = '''
                        <p style="font-size: 12px; margin-bottom: 4px;">Confirm Password</p>
                        <div class="input-field">[Input Field]</div>
                    ''' if is_reg else ""
                    
                    section_html += f'''
                        <div class="flex" style="justify-content: center; padding: 40px 0;">
                            <div class="auth-card-container col">
                                <div class="section-title" style="text-align: center;">{label}</div>
                                <p style="font-size: 12px; margin-bottom: 4px;">Email</p>
                                <div class="input-field">[Input Field]</div>
                                <p style="font-size: 12px; margin-bottom: 4px;">Password</p>
                                <div class="input-field">[Input Field]</div>
                                {confirm_field}
                                <div class="flex" style="justify-content: space-between; align-items: center; margin-bottom: 24px;">
                                    <label style="font-size: 12px;"><input type="checkbox"> Remember me</label>
                                    <p style="font-size: 12px; text-decoration: underline;">Forgot password</p>
                                </div>
                                <div class="btn btn-primary" style="width: 100%; margin-bottom: 16px;">Continue</div>
                                <div class="separator"><span>OR</span></div>
                                <div class="btn" style="width: 100%; margin-bottom: 16px;">Continue with Google</div>
                            </div>
                        </div>
                    '''
                elif ctype == "Button":
                    btn_class = "btn-primary" if "Continue" in label or "Submit" in label else "btn"
                    section_html += f'<a href="{link_url}" class="{btn_class}" style="text-decoration:none;">{label}</a>'
                elif ctype == "Input":
                    section_html += f'<div class="col"><p style="font-size: 12px; margin-bottom: 4px;">{label}</p><div class="input-field">[{subtext or "Input Field"}]</div></div>'
                elif ctype == "Card":
                    section_html += f'<div class="col" style="border: 1px solid var(--border-color); padding: 16px; border-radius: 8px;"><div class="section-title">{label}</div><div class="placeholder-box" style="height:100px;">[Copy: {content[:50]}...]</div><p class="annotation">{subtext}</p></div>'
                elif ctype == "Link":
                    section_html += f'<a href="{link_url}" style="font-size: 12px; text-decoration: underline; color: var(--text-secondary); margin-bottom: 4px; display:block;">{label}</a>'
                else:
                    section_html += f'<div class="placeholder-box">{label}</div>'

            if s_type == "Sidebar":
                pass 
            elif s_type == "Header":
                pass 
            elif s_type == "SubHeader":
                 main_content_html += f'<div class="grid grid-3">{section_html}</div>'
            elif s_type == "Footer":
                 footer_html += f'<div class="grid grid-4" style="margin-top: 40px; border-top: 1px solid var(--border-color); padding-top: 20px;">{section_html}</div>'
            else:
                main_content_html += section_html

        layout_body = ""
        if is_dashboard:
            layout_body = f'''
                <div class="flex">
                    <div class="col sidebar">
                        <div class="section-title">Navigation</div>
                        {sidebar_html}
                    </div>
                    <div class="col flex-1">
                        {main_content_html}
                    </div>
                </div>
            '''
        else:
            layout_body = main_content_html

        screen_name = wf.get("screen", "Screen")
        screen_purpose = wf.get("purpose", "")
        screen_flow = wf.get("flow", "N/A")
        screen_key = wf.get("screenKey", "")

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen_name} - Wireframe</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="wireframe-container">
        <div class="screen-card">
            <header>
                <div class="screen-info">
                    <h1>{screen_name}</h1>
                    <p>{screen_purpose}</p>
                </div>
                <div class="nav-links">
                    {top_nav_links}
                    <div style="width:1px; height:24px; background:var(--border-color); margin:0 8px;"></div>
                    {header_nav_html}
                </div>
            </header>
            
            {layout_body}
            
            {footer_html}

            <footer style="margin-top: 40px; border-top: 1px solid var(--border-color); padding-top: 20px;">
                <p class="annotation">Flow: {screen_flow} | Screen: {screen_key}</p>
            </footer>
        </div>
    </div>
</body>
</html>
"""

    def generate_index(self, screens: List[Dict[str, Any]]) -> str:
        links_html = "".join([f'<li><a href="{s["url"]}">{s["name"]}</a></li>' for s in screens])
        
        # Use a non-f-string for the template to avoid double-curly brace confusion in CSS
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Wireframe Navigation</title>
    <link rel="stylesheet" href="style.css">
    <style>
        ul { list-style: none; margin-top: 32px; }
        li { margin-bottom: 12px; }
        a { color: #121212; text-decoration: none; font-weight: 500; font-size: 18px; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="wireframe-container">
        <div class="screen-card">
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: 8px;">Project Wireframes</h1>
            <p style="color: var(--text-secondary);">Select a screen to view its low-fidelity structure.</p>
            <ul>{{links}}</ul>
        </div>
    </div>
</body>
</html>
"""
        return template.replace("{{links}}", links_html)
