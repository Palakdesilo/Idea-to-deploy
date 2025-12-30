import json
from pathlib import Path
from typing import Dict, List, Any

class UIRenderer:
    def __init__(self):
        self.default_tokens = {
            "colors": {
                "primary": "#4f46e5",
                "background": "#f8f9fa",
                "card_bg": "#ffffff",
                "text_main": "#1a1a1a",
                "accent": "#6366f1"
            },
            "radius": { "large": "12px", "medium": "8px", "small": "4px" },
            "shadows": { "soft": "0 4px 12px rgba(0,0,0,0.05)", "card": "0 1px 3px rgba(0,0,0,0.1)" }
        }

    def render_project(self, project_id: str, wireframes: List[Dict[str, Any]], ui_design: Dict[str, Any]):
        output_dir = Path(__file__).parent.parent / "data" / "artifacts" / project_id / "ui"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tokens = ui_design.get("design_tokens", self.default_tokens)
        colors = tokens.get("colors", self.default_tokens["colors"])
        radius = tokens.get("radius", self.default_tokens["radius"])
        shadows = tokens.get("shadows", self.default_tokens["shadows"])
        
        css = f"""
:root {{
    --primary: {colors.get('primary', '#4f46e5')};
    --bg-color: {colors.get('background', '#f8f9fa')};
    --card-bg: {colors.get('card_bg', '#ffffff')};
    --text-primary: {colors.get('text_main', '#1a1a1a')};
    --text-secondary: #71717a;
    --border-color: #e4e4e7;
    --radius-lg: {radius.get('large', '12px')};
    --radius-md: {radius.get('medium', '8px')};
    --shadow-sm: {shadows.get('card', '0 1px 2px rgba(0,0,0,0.05)')};
    --shadow-md: {shadows.get('soft', '0 4px 6px rgba(0,0,0,0.05)')};
    --font-family: 'Inter', system-ui, sans-serif;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
    background-color: var(--bg-color);
    font-family: var(--font-family);
    color: var(--text-primary);
    padding: 40px;
    line-height: 1.6;
}}

.ui-container {{
    max-width: 1200px;
    margin: 0 auto;
}}

.screen-card {{
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 40px;
    margin-bottom: 40px;
    box-shadow: var(--shadow-md);
}}

header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
}}

.screen-info h1 {{ font-size: 24px; font-weight: 700; color: var(--text-primary); }}
.screen-info p {{ font-size: 14px; color: var(--text-secondary); }}

.nav-links {{ display: flex; gap: 16px; align-items: center; }}

.btn {{
    padding: 10px 20px;
    border-radius: var(--radius-md);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid var(--border-color);
    background: white;
    color: var(--text-primary);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}}

.btn-primary {{
    background: var(--primary);
    color: white;
    border: none;
}}

.btn-primary:hover {{ filter: brightness(1.1); }}

.input-field {{
    width: 100%;
    padding: 12px 16px;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    font-size: 14px;
    margin-bottom: 16px;
    background: #ffffff;
    transition: border-color 0.2s;
}}

.input-field:focus {{ outline: none; border-color: var(--primary); ring: 2px var(--primary); }}

.sidebar {{
    width: 240px;
    border-right: 1px solid var(--border-color);
    padding-right: 24px;
    flex-shrink: 0;
}}

.flex {{ display: flex; gap: 24px; }}
.col {{ display: flex; flex-direction: column; gap: 12px; }}
.flex-1 {{ flex: 1; }}

.card {{
    background: white;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 20px;
    box-shadow: var(--shadow-sm);
}}

.grid {{ display: grid; gap: 24px; }}
.grid-3 {{ grid-template-columns: repeat(3, 1fr); }}

.auth-card-container {{ width: 440px; padding: 48px; margin: 40px auto; }}
.separator {{ position: relative; text-align: center; margin: 24px 0; }}
.separator::before {{ content: ""; position: absolute; top: 50%; left: 0; right: 0; border-top: 1px solid var(--border-color); }}
.separator span {{ position: relative; background: white; padding: 0 12px; font-size: 12px; color: var(--text-secondary); }}

table {{ width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; }}
th {{ text-align: left; padding: 12px; border-bottom: 2px solid var(--border-color); color: var(--text-secondary); font-weight: 600; }}
td {{ padding: 16px 12px; border-bottom: 1px solid var(--border-color); }}

.avatar {{ width: 40px; height: 40px; border-radius: 50%; background: var(--border-color); overflow: hidden; }}
.skeleton {{ background: #f1f5f9; border-radius: 4px; }}
"""
        with open(output_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(css)

        screens_list = []
        for wf in wireframes:
            html = self.generate_html(wf, tokens)
            filename = f"{wf.get('screenKey', 'screen')}.html"
            with open(output_dir / filename, "w", encoding="utf-8") as f:
                f.write(html)
            screens_list.append({
                "name": wf.get("screen"),
                "url": filename
            })

        index_html = self.generate_index(screens_list)
        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(index_html)

    def generate_html(self, wf: Dict[str, Any], tokens: Dict[str, Any]) -> str:
        sidebar_html = ""
        header_nav_html = ""
        main_content_html = ""
        
        is_dashboard = (wf.get("shellType") == "Internal") or any(x in wf.get("screen", "") for x in ["Dashboard", "Feed", "Home", "Analytics", "Timeline", "Gallery", "Matrix", "History", "Skill"])

        for section in wf.get("layout", []):
            s_type = section.get("section", "Main")
            section_html = ""
            
            for comp in section.get("components", []):
                ctype = comp.get("type", "Box")
                label = comp.get("label", "Label")
                
                if ctype == "ProfileCircle":
                    header_nav_html += f'<div class="avatar" title="{label}"><img src="https://api.dicebear.com/7.x/avataaars/svg?seed={label}" alt="avatar"></div>'
                elif ctype == "SearchBar":
                    header_nav_html += f'<div style="flex:1; max-width:400px;"><input type="text" class="input-field" placeholder="Search..." style="margin-bottom:0;"></div>'
                elif ctype == "Link" and s_type == "Header":
                    header_nav_html += f'<a href="#" class="btn" style="border:none;">{label}</a>'
                elif ctype == "Button" and s_type == "Header":
                    header_nav_html += f'<a href="#" class="btn btn-primary">{label}</a>'
                elif ctype == "Button" and s_type == "Sidebar":
                    sidebar_html += f'<a href="#" class="btn" style="border:none; justify-content:flex-start; width:100%;">{label}</a>'
                elif ctype == "StatCard":
                    section_html += f'''
                        <div class="card col">
                            <span style="font-size:12px; color:var(--text-secondary); font-weight:600;">{label}</span>
                            <span style="font-size:24px; font-weight:700;">$0.00</span>
                            <span style="font-size:12px; color:#10b981;">+0.0% from last month</span>
                        </div>
                    '''
                elif ctype == "PostCard":
                    section_html += f'''
                        <div class="card col" style="margin-bottom:24px;">
                            <div class="flex" style="align-items:center; gap:12px;">
                                <div class="avatar"><img src="https://api.dicebear.com/7.x/avataaars/svg?seed={label}" alt="user"></div>
                                <div class="col" style="gap:2px;">
                                    <span style="font-weight:600; font-size:14px;">User Name</span>
                                    <span style="font-size:12px; color:var(--text-secondary);">2 hours ago</span>
                                </div>
                            </div>
                            <p style="font-size:15px; margin: 12px 0;">{label}</p>
                            <div class="skeleton" style="height:200px; width:100%;"></div>
                            <div class="flex" style="padding-top:12px; border-top:1px solid var(--border-color); margin-top:12px;">
                                <button class="btn" style="border:none; font-size:13px; gap:6px;">Like</button>
                                <button class="btn" style="border:none; font-size:13px; gap:6px;">Comment</button>
                                <button class="btn" style="border:none; font-size:13px; gap:6px; margin-left:auto;">Share</button>
                            </div>
                        </div>
                    '''
                elif ctype == "Table":
                    section_html += f'''
                        <div class="col" style="margin-top:24px;">
                            <h3 style="font-size:18px; margin-bottom:8px;">{label}</h3>
                            <div class="card" style="padding:0; overflow:hidden;">
                                <table>
                                    <thead>
                                        <tr><th>Item</th><th>Status</th><th>Date</th><th>Amount</th></tr>
                                    </thead>
                                    <tbody>
                                        <tr><td>Example Row 1</td><td><span style="padding:4px 8px; border-radius:12px; background:#fef3c7; color:#92400e; font-size:11px; font-weight:700;">PENDING</span></td><td>Dec 30, 2025</td><td>$240.00</td></tr>
                                        <tr><td>Example Row 2</td><td><span style="padding:4px 8px; border-radius:12px; background:#dcfce7; color:#166534; font-size:11px; font-weight:700;">COMPLETED</span></td><td>Dec 29, 2025</td><td>$1,200.00</td></tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    '''
                elif ctype == "AuthCard":
                    is_reg = "Register" in label or "Sign Up" in label or "Register" in wf.get("screen", "")
                    confirm_field = '''
                        <div class="col" style="gap:6px; margin-bottom:16px;">
                            <label style="font-size:13px; font-weight:600;">Confirm Password</label>
                            <input type="password" class="input-field" placeholder="••••••••" style="margin-bottom:0;">
                        </div>
                    ''' if is_reg else ""
                    
                    section_html += f'''
                        <div class="card auth-card-container col">
                            <h2 style="font-size:24px; font-weight:700; text-align:center;">{label}</h2>
                            <p style="text-align:center; color:var(--text-secondary); margin-bottom:32px;">Please enter your details to continue</p>
                            
                            <div class="col" style="gap:6px; margin-bottom:16px;">
                                <label style="font-size:13px; font-weight:600;">Email Address</label>
                                <input type="email" class="input-field" placeholder="name@example.com" style="margin-bottom:0;">
                            </div>
                            
                            <div class="col" style="gap:6px; margin-bottom:16px;">
                                <div class="flex" style="justify-content:space-between; align-items:center;">
                                    <label style="font-size:13px; font-weight:600;">Password</label>
                                    <a href="#" style="font-size:12px; color:var(--primary);">Forgot?</a>
                                </div>
                                <input type="password" class="input-field" placeholder="••••••••" style="margin-bottom:0;">
                            </div>
                            
                            {confirm_field}
                            
                            <button class="btn btn-primary" style="width:100%; margin-top:8px;">Continue</button>
                            
                            <div class="separator"><span>OR</span></div>
                            
                            <button class="btn" style="width:100%; gap:8px;">
                                <img src="https://www.google.com/favicon.ico" width="16" height="16">
                                Sign in with Google
                            </button>
                        </div>
                    '''
                elif ctype == "TimelineItem":
                    section_html += f'''
                        <div class="flex" style="gap:24px; position:relative; margin-bottom:12px;">
                            <div class="col" style="align-items:center;">
                                <div style="width:14px; height:14px; border-radius:50%; background:var(--primary); box-shadow:0 0 0 4px rgba(79, 70, 229, 0.1); z-index:2;"></div>
                                <div style="width:2px; flex:1; background:linear-gradient(to bottom, var(--border-color), transparent); margin: 4px 0;"></div>
                            </div>
                            <div class="card flex-1" style="margin-bottom:20px; border-left: 4px solid var(--primary);">
                                <div class="flex" style="justify-content:space-between; align-items:flex-start;">
                                    <div class="col" style="gap:4px;">
                                        <h4 style="font-size:17px; font-weight:700; color:var(--text-primary);">{label}</h4>
                                        <p style="font-size:13px; font-weight:500; color:var(--primary);">{comp.get("annotation", "Achievement Node")}</p>
                                    </div>
                                    <span style="font-size:11px; font-weight:700; background:rgba(79, 70, 229, 0.05); border:1px solid rgba(79, 70, 229, 0.1); padding:4px 10px; border-radius:20px; color:var(--primary);">2024 - 2025</span>
                                </div>
                                <p style="font-size:14px; color:var(--text-secondary); margin-top:12px; line-height:1.5;">Successfully led the transition to a micro-frontend architecture, improving deployment speed by 40% and enhancing overall system stability.</p>
                            </div>
                        </div>
                    '''
                elif ctype == "SkillItem":
                    section_html += f'''
                        <div style="display:inline-flex; align-items:center; gap:10px; padding:10px 20px; background:white; border:1px solid var(--border-color); border-radius:30px; margin-right:12px; margin-bottom:12px; box-shadow:var(--shadow-sm); transition: transform 0.2s; cursor:default;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="width:10px; height:10px; border-radius:50%; background:var(--primary); box-shadow: 0 0 8px var(--primary);"></div>
                            <span style="font-size:14px; font-weight:600; color:var(--text-primary);">{label}</span>
                        </div>
                    '''
                elif ctype == "ProjectCard":
                    section_html += f'''
                        <div class="card col" style="padding:0; overflow:hidden; margin-bottom:24px;">
                            <div class="skeleton" style="height:180px; width:100%; display:flex; align-items:center; justify-content:center; background:linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); color:#dee2e6;">
                                <span style="font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:0.1em;">Project Preview</span>
                            </div>
                            <div class="col" style="padding:20px;">
                                <div class="flex" style="justify-content:space-between; align-items:center;">
                                    <h4 style="font-size:18px; font-weight:700;">{label}</h4>
                                    <span style="font-size:11px; background:var(--bg-color); padding:4px 8px; border-radius:4px; font-weight:600;">Case Study</span>
                                </div>
                                <p style="font-size:14px; color:var(--text-secondary); margin:12px 0;">Comprehensive overview of the design process, technical challenges, and final outcomes for this specific project.</p>
                                <div class="flex" style="gap:8px;">
                                    <div style="font-size:11px; padding:2px 8px; background:#f1f5f9; border-radius:4px; color:#64748b;">React</div>
                                    <div style="font-size:11px; padding:2px 8px; background:#f1f5f9; border-radius:4px; color:#64748b;">Node.js</div>
                                </div>
                            </div>
                        </div>
                    '''
                elif ctype == "Button":
                    btn_class = "btn-primary" if "Continue" in label or "Submit" in label else "btn"
                    section_html += f'<button class="{btn_class}">{label}</button>'
                elif ctype == "Input":
                    section_html += f'<div class="col" style="gap:6px;"><label style="font-size:13px; font-weight:600;">{label}</label><input type="text" class="input-field" placeholder="Enter value..."></div>'
                elif ctype == "Card":
                    section_html += f'''
                        <div class="card col" style="padding: 24px; border-top: 4px solid var(--primary); transition: box-shadow 0.3s;">
                            <div class="flex" style="align-items: center; gap: 12px; margin-bottom: 12px;">
                                <div style="width: 32px; height: 32px; border-radius: 8px; background: rgba(79, 70, 229, 0.1); display: flex; align-items: center; justify-content: center; color: var(--primary);">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                                </div>
                                <h4 style="font-size: 17px; font-weight: 700;">{label}</h4>
                            </div>
                            <p style="font-size: 14px; color: var(--text-secondary); line-height: 1.5;">{comp.get("annotation", "Standard descriptive text providing more context about this specific design element or content block.")}</p>
                            <div class="flex" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #f1f5f9; gap: 12px; font-size: 12px; color: var(--text-secondary);">
                                <span>Updated: Dec 30</span>
                                <span>•</span>
                                <span style="color: var(--primary); font-weight: 600; cursor: pointer;">View Details →</span>
                            </div>
                        </div>
                    '''
                else:
                    section_html += f'''
                        <div class="card" style="background: #ffffff; padding: 20px; display: flex; align-items: center; gap: 16px;">
                            <div style="width: 8px; height: 32px; background: #e2e8f0; border-radius: 4px;"></div>
                            <div class="col" style="gap: 4px;">
                                <span style="font-size: 14px; font-weight: 600;">{label}</span>
                                <span style="font-size: 12px; color: var(--text-secondary);">System Metadata Component</span>
                            </div>
                        </div>
                    '''

            if s_type == "SubHeader":
                 main_content_html += f'<div class="grid grid-3" style="margin-bottom:32px;">{section_html}</div>'
            else:
                main_content_html += f'<div class="grid grid-2" style="gap: 20px;">{section_html}</div>'

        layout_body = ""
        if is_dashboard:
            layout_body = f'''
                <div class="flex">
                    <div class="sidebar col">
                        <div style="font-size:12px; font-weight:800; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">Menu</div>
                        {sidebar_html}
                    </div>
                    <div class="flex-1 col">
                        {main_content_html}
                    </div>
                </div>
            '''
        else:
            layout_body = main_content_html

        screen_name = wf.get("screen", "Screen")
        screen_purpose = wf.get("purpose", "")

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen_name} - Visual UI</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="ui-container">
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
        </div>
    </div>
</body>
</html>
"""

    def generate_index(self, screens: List[Dict[str, Any]]) -> str:
        links_html = "".join([f'<li><a href="{s["url"]}">{s["name"]}</a></li>' for s in screens])
        template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Visual UI Navigation</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="ui-container">
        <div class="screen-card">
            <h1 style="font-size: 32px; font-weight: 800; margin-bottom: 8px;">Project UI Prototypes</h1>
            <p style="color: var(--text-secondary); margin-bottom: 24px;">Select a screen to view its high-fidelity visual design.</p>
            <ul style="list-style: none;">{{links}}</ul>
        </div>
    </div>
</body>
</html>
"""
        return template.replace("{{links}}", links_html)
