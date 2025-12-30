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
        output_dir = Path(__file__).parent.parent / "data" / "artifacts" / project_id / "wireframes"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(self.css_content)
            
        screens = []
        for wf in wireframes_json:
            html = self.generate_html(wf)
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

    def generate_html(self, wf: Dict[str, Any]) -> str:
        sidebar_html = ""
        header_nav_html = ""
        main_content_html = ""
        
        is_dashboard = any(x in wf.get("screen", "") for x in ["Dashboard", "Feed", "Home", "Analytics"])

        for section in wf.get("layout", []):
            s_type = section.get("section", "Main")
            section_html = ""
            
            for comp in section.get("components", []):
                ctype = comp.get("type", "Box")
                label = comp.get("label", "Label")
                annot = comp.get("annotation", "")
                
                if ctype == "ProfileCircle":
                    header_nav_html += f'<div class="placeholder-box" style="width:36px; height:36px; border-radius:50%;" title="{label}"></div>'
                elif ctype == "SearchBar":
                    header_nav_html += f'<div class="col" style="width:200px;"><div class="placeholder-box" style="height:34px; min-height:34px;">[Search Bar]</div></div>'
                elif ctype == "Link" and s_type == "Header":
                    header_nav_html += f'<div class="btn">{label}</div>'
                elif ctype == "Button" and s_type == "Header":
                    header_nav_html += f'<div class="btn btn-primary">{label}</div>'
                elif ctype == "Button" and s_type == "Sidebar":
                    sidebar_html += f'<div class="btn" style="text-align:left;">{label}</div>'
                elif ctype == "StatCard":
                    section_html += f'''
                        <div class="col" style="border: 1px solid var(--border-color); padding: 16px; border-radius: 8px;">
                            <div class="section-title">Stat Card</div>
                            <div class="placeholder-box" style="height: 60px; font-size: 20px;">[Value]</div>
                            <p class="annotation">{label}</p>
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
                            <div class="placeholder-box" style="height: 120px; margin-bottom: 16px;">[{label}]</div>
                            <div class="flex">
                                <div class="btn" style="font-size:11px;">[Action 1]</div>
                                <div class="btn" style="font-size:11px;">[Action 2]</div>
                                <div class="btn btn-primary" style="font-size:11px;">[Primary Action]</div>
                            </div>
                        </div>
                    '''
                elif ctype == "Table":
                    section_html += f'''
                        <div class="col">
                            <div class="section-title">{label}</div>
                            <table>
                                <thead>
                                    <tr><th>Post</th><th>Type</th><th>Status</th><th>Action</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td>Row 1</td><td>Free</td><td>Active</td><td><span style="text-decoration:underline;">View</span></td></tr>
                                    <tr><td>Row 2</td><td>Paid</td><td>Draft</td><td><span style="text-decoration:underline;">Edit</span></td></tr>
                                </tbody>
                            </table>
                        </div>
                    '''
                elif ctype == "AuthCard":
                    is_reg = "Register" in label or "Sign Up" in label or "Register" in wf.get("screen", "")
                    confirm_field = '''
                        <p style="font-size: 12px; margin-bottom: 4px;">Confirm Password</p>
                        <div class="input-field">[Input Field]</div>
                    ''' if is_reg else ""
                    
                    section_html += f'''
                        <div class="flex" style="justify-content: center; padding: 40px 0;">
                            <div class="auth-card-container col">
                                <div class="section-title" style="text-align: center;">Auth Card</div>
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
                                <p class="annotation" style="text-align: center;">{label}</p>
                            </div>
                        </div>
                    '''
                elif ctype == "ProjectCard":
                    section_html += f'''
                        <div class="col" style="border: 1px solid var(--border-color); padding: 0; border-radius: 8px; margin-bottom: 20px; overflow:hidden;">
                            <div class="placeholder-box" style="height: 120px;">[Project Preview Placeholder]</div>
                            <div class="col" style="padding:16px;">
                                <div class="section-title">{label}</div>
                                <div class="placeholder-box" style="height: 40px; font-size:12px;">[Project Abstract]</div>
                                <div class="flex" style="gap:8px; margin-top:8px;">
                                    <div class="placeholder-box" style="padding:2px 8px; font-size:10px;">[Tag 1]</div>
                                    <div class="placeholder-box" style="padding:2px 8px; font-size:10px;">[Tag 2]</div>
                                </div>
                            </div>
                        </div>
                    '''
                elif ctype == "TimelineItem":
                    section_html += f'''
                        <div class="flex" style="gap:16px;">
                            <div class="col" style="align-items:center; width:20px;">
                                <div class="placeholder-box" style="width:10px; height:10px; min-height:10px; border-radius:50%; background:var(--text-secondary);"></div>
                                <div style="width:1px; flex:1; background:var(--border-color);"></div>
                            </div>
                            <div class="col flex-1" style="border:1px solid var(--border-color); padding:12px; border-radius:4px; margin-bottom:12px;">
                                <div class="section-title">{label}</div>
                                <div class="placeholder-box" style="height:40px;">[Timeline Evidence]</div>
                                <p class="annotation">{annot}</p>
                            </div>
                        </div>
                    '''
                elif ctype == "SkillItem":
                    section_html += f'''
                        <div class="placeholder-box" style="display:inline-block; padding:4px 12px; border-radius:20px; margin:0 4px 8px 0;">{label}</div>
                    '''
                elif ctype == "Button":
                    btn_class = "btn-primary" if "Continue" in label or "Submit" in label else "btn"
                    section_html += f'<div class="{btn_class}">{label}</div>'
                elif ctype == "Input":
                    section_html += f'<div class="col"><p style="font-size: 12px; margin-bottom: 4px;">{label}</p><div class="input-field">[Input Field]</div></div>'
                elif ctype == "Card":
                    section_html += f'<div class="col" style="border: 1px solid var(--border-color); padding: 16px; border-radius: 8px;"><div class="section-title">{label}</div><div class="placeholder-box" style="height:100px;">{annot}</div></div>'
                else:
                    section_html += f'<div class="placeholder-box">{label}</div>'

            if s_type == "Sidebar":
                pass 
            elif s_type == "Header":
                pass 
            elif s_type == "SubHeader":
                 main_content_html += f'<div class="grid grid-3">{section_html}</div>'
            else:
                main_content_html += section_html

        layout_body = ""
        if is_dashboard:
            layout_body = f'''
                <div class="flex">
                    <div class="col sidebar">
                        <div class="section-title">Sidebar</div>
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
                    {header_nav_html}
                </div>
            </header>
            
            {layout_body}

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
