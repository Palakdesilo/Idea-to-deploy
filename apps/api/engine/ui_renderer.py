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
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --radius-lg: 16px;
    --radius-md: 12px;
    --shadow-soft: 0 4px 20px -2px rgba(0,0,0,0.05);
    --shadow-card: 0 10px 15px -3px rgba(0,0,0,0.1);
    --font-family: 'Outfit', 'Inter', sans-serif;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ background-color: var(--bg-color); font-family: var(--font-family); color: var(--text-primary); line-height: 1.5; }}
.ui-container {{ max-width: 1400px; margin: 0 auto; }}
.screen-card {{ background: var(--card-bg); min-height: 100vh; display: flex; flex-direction: column; overflow: hidden; }}

/* Navigation */
header {{ display: flex; justify-content: space-between; align-items: center; padding: 24px 60px; background: white; border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; }}
.logo {{ font-size: 24px; font-weight: 800; letter-spacing: -0.05em; text-transform: uppercase; }}
.nav-links {{ display: flex; gap: 32px; align-items: center; }}
.nav-links a {{ text-decoration: none; color: var(--text-primary); font-weight: 600; font-size: 14px; transition: opacity 0.2s; }}
.nav-links a:hover {{ opacity: 0.7; }}

/* Components */
.section-padding {{ padding: 80px 60px; }}
.hero {{ padding: 120px 60px; text-align: center; background: #000; color: #fff; position: relative; overflow: hidden; }}
.split-section {{ display: grid; grid-template-columns: 1fr 1fr; align-items: center; gap: 60px; }}
.split-section.reverse {{ direction: rtl; }}
.split-section.reverse > * {{ direction: ltr; }}

.grid {{ display: grid; gap: 32px; }}
.grid-2 {{ grid-template-columns: repeat(2, 1fr); }}
.grid-3 {{ grid-template-columns: repeat(3, 1fr); }}
.grid-4 {{ grid-template-columns: repeat(4, 1fr); }}

.product-card {{ background: white; border-radius: var(--radius-md); overflow: hidden; transition: transform 0.3s; cursor: pointer; border: 1px solid var(--border-color); }}
.product-card:hover {{ transform: translateY(-8px); box-shadow: var(--shadow-card); }}
.product-img {{ height: 300px; background: #f1f5f9; display: flex; align-items: center; justify-content: center; color: #94a3b8; font-weight: 700; }}

.testimonial-card {{ background: #f8fafc; padding: 32px; border-radius: var(--radius-lg); }}
.stars {{ color: #fbbf24; margin-bottom: 12px; }}

.newsletter {{ background: var(--primary); color: white; padding: 80px 20px; text-align: center; border-radius: var(--radius-lg); margin: 0 60px 80px; }}
.newsletter h2 {{ font-size: 32px; font-weight: 800; margin-bottom: 16px; }}
.newsletter input {{ padding: 16px 24px; border-radius: 30px; border: none; width: 300px; margin-right: 12px; }}

.btn {{ padding: 14px 28px; border-radius: 30px; font-weight: 700; text-decoration: none; display: inline-block; transition: all 0.2s; cursor: pointer; border: none; }}
.btn-primary {{ background: var(--primary); color: white; }}
.btn-outline {{ background: transparent; border: 2px solid currentColor; color: inherit; }}

footer {{ background: #1a1a1a; color: #94a3b8; padding: 80px 60px; margin-top: auto; }}
.footer-grid {{ display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 40px; }}
.footer-logo {{ color: #fff; font-size: 20px; font-weight: 800; margin-bottom: 24px; }}
.footer-col h4 {{ color: #fff; margin-bottom: 24px; text-transform: uppercase; font-size: 13px; letter-spacing: 0.1em; }}
.footer-col ul {{ list-style: none; }}
.footer-col li {{ margin-bottom: 12px; font-size: 14px; cursor: pointer; }}
.footer-col li:hover {{ color: #fff; }}

.stat-item {{ text-align: center; border-right: 1px solid var(--border-color); }}
.stat-item:last-child {{ border-right: none; }}
"""
        with open(output_dir / "style.css", "w", encoding="utf-8") as f:
            f.write(css)

        screens_list = []
        for wf in wireframes:
            try:
                html = self.generate_html(wf, tokens, wireframes)
                screen_key = wf.get('screenKey', 'screen')
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

    def generate_html(self, wf: Dict[str, Any], tokens: Dict[str, Any], all_screens: List[Dict[str, Any]]) -> str:
        screen_name = wf.get("screen", "Screen")
        is_app = any(x in screen_name.lower() for x in ["dashboard", "feed", "profile", "setting", "admin", "analytics", "home", "chat", "list", "detail"]) and "landing" not in screen_name.lower()
        
        nav_map = { s.get("screen", "").lower(): f"{s.get('screenKey')}.html" for s in all_screens if s.get("screenKey") }
        nav_map.update({ s.get("screenKey", "").lower(): f"{s.get('screenKey')}.html" for s in all_screens if s.get("screenKey") })

        # --- LAYOUT OVERRIDES FOR VISUAL RELIABILITY ---
        # Forces specific component structures for core screens to prevent "empty" or "generic" look
        lower_screen = screen_name.lower()
        
        if "login" in lower_screen or "register" in lower_screen or "sign in" in lower_screen or "sign up" in lower_screen:
            # Force Auth Layout
            wf["layout"] = [
                {"section": "Header", "components": [{"type": "Header", "label": "Product"}]},
                {"section": "Auth", "components": [{"type": "AuthCard", "label": screen_name}]},
                {"section": "Footer", "components": [{"type": "Footer", "label": "Footer"}]}
            ]
        
        elif "feed" in lower_screen or "home" in lower_screen:
            # Force Feed Layout if seemingly empty or generic
            has_feed = any("feed" in json.dumps(bg).lower() for bg in wf.get("layout", []))
            if not has_feed: # Only override if specific feed components aren't already detected
                wf["layout"] = [
                    {"section": "Header", "components": [{"type": "Header", "label": screen_name}]},
                    {"section": "Sidebar", "components": [{"type": "Sidebar", "label": "Nav"}]},
                    {"section": "FeedContent", "components": [{"type": "PostCard", "label": "Community Feed", "content": "feed_smart_injection"}]} 
                ]
                
        elif "alert" in lower_screen or "notification" in lower_screen:
             wf["layout"] = [
                {"section": "Header", "components": [{"type": "Header", "label": screen_name}]},
                {"section": "Sidebar", "components": [{"type": "Sidebar", "label": "Nav"}]},
                {"section": "Alerts", "components": [{"type": "Table", "label": "Recent Notifications", "content": [{"item": "System Update", "date": "Just now", "status": "Critical"}, {"item": "New Login", "date": "2 mins ago", "status": "Info"}, {"item": "Server Backup", "date": "1h ago", "status": "Success"}]}]} 
            ]
        # -----------------------------------------------

        # CSS Constants for App Layout
        app_css = """
        .app-layout { display: flex; height: 100vh; background: #f3f4f6; }
        .sidebar { width: 260px; background: white; border-right: 1px solid var(--border-color); display: flex; flex-direction: column; padding: 24px; flex-shrink: 0; }
        .sidebar-logo { font-size: 20px; font-weight: 800; margin-bottom: 40px; color: var(--primary); display: flex; align-items: center; gap: 10px; }
        .sidebar-menu { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { display: flex; align-items: center; gap: 12px; padding: 12px; color: var(--text-secondary); text-decoration: none; border-radius: 8px; font-weight: 500; font-size: 14px; transition: all 0.2s; }
        .menu-item:hover, .menu-item.active { background: #eef2ff; color: var(--primary); }
        .app-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .top-bar { height: 64px; background: white; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; padding: 0 32px; flex-shrink: 0; }
        .page-content { flex: 1; overflow-y: auto; padding: 32px; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 24px; }
        .widget { background: white; border-radius: 16px; padding: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.05); }
        .col-span-12 { grid-column: span 12; }
        .col-span-8 { grid-column: span 8; }
        .col-span-6 { grid-column: span 6; }
        .col-span-4 { grid-column: span 4; }
        .col-span-3 { grid-column: span 3; }
        
        .avatar { width: 40px; height: 40px; border-radius: 50%; background: #e0e7ff; display: flex; align-items: center; justify-content: center; color: var(--primary); font-weight: 700; font-size: 14px; }
        .status-badge { padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
        .status-success { background: #dcfce7; color: #166534; }
        """

        # Generate Content based on Layout Type
        content_html = ""
        header_links = ""
        for s in all_screens[:5]:
            if "landing" not in s.get("screen", "").lower():
                header_links += f'<a href="{s.get("screenKey")}.html">{s.get("screen")}</a>'
        
        for section in wf.get("layout", []):
            if section.get("section") in ["Header", "Footer"] and is_app: continue
            
            section_html = ""
            for comp in section.get("components", []):
                ctype = comp.get("type", "").lower()
                label = comp.get("label", "")
                content = comp.get("content", "")
                subtext = comp.get("subtext", "View")
                link_url = nav_map.get(subtext.lower(), "#")
                
                # UNIVERSAL COMPONENT RENDERERS
                if ctype == "authcard":
                    # Realistic Login/Register Form
                    is_register = "register" in label.lower() or "sign up" in label.lower()
                    title = "Create an account" if is_register else "Welcome back"
                    subtitle = "Enter your details to get started." if is_register else "Please enter your details to sign in."
                    btn_text = "Sign Up" if is_register else "Sign In"
                    switch_text = "Already have an account? Sign in" if is_register else "Don't have an account? Sign up"
                    switch_link = "login.html" if is_register else "register.html"

                    section_html += f'''
                    <div style="max-width: 400px; margin: 80px auto; padding: 40px; background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                        <div style="font-size: 24px; font-weight: 800; margin-bottom: 8px; color: #0f172a;">{title}</div>
                        <p style="color: #64748b; margin-bottom: 32px; font-size: 14px;">{subtitle}</p>
                        
                        <div style="text-align: left; margin-bottom: 16px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 8px;">Email Address</label>
                            <input type="email" placeholder="name@company.com" style="width: 100%; padding: 12px 16px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s;">
                        </div>
                        
                        <div style="text-align: left; margin-bottom: 24px;">
                            <label style="display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 8px;">Password</label>
                            <input type="password" placeholder="••••••••" style="width: 100%; padding: 12px 16px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s;">
                        </div>
                        
                        <button class="btn btn-primary" style="width: 100%; justify-content: center; margin-bottom: 24px;">{btn_text}</button>
                        
                        <a href="{switch_link}" style="font-size: 13px; color: #64748b; text-decoration: none; font-weight: 500;">{switch_text}</a>
                    </div>
                    '''

                elif ctype == "table":
                    rows = ""
                    try:
                        data = json.loads(content) if isinstance(content, str) else content
                        for d in data[:5]:
                            rows += f'''<tr style="border-bottom: 1px solid #f1f5f9; transition: background 0.1s;">
                                <td style="padding: 16px;">
                                    <div style="font-weight: 600; color: #1e293b;">{d.get('item', 'Item')}</div>
                                </td>
                                <td style="padding: 16px; color: #64748b;">{d.get('date', 'Oct 24, 2025')}</td>
                                <td style="padding: 16px;"><span class="status-badge status-success">{d.get('status', 'Active')}</span></td>
                                <td style="padding: 16px; text-align: right;"><a href="#" style="color: var(--primary); font-weight: 600; font-size: 13px; text-decoration: none;">Manage</a></td>
                            </tr>'''
                    except: rows = "<tr><td colspan='4' style='padding:24px; text-align:center;'>No data available</td></tr>"

                    section_html += f'''
                    <div class="widget col-span-12" style="padding: 0; overflow: hidden; margin-bottom: 24px;">
                        <div style="padding: 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;">
                            <h3 style="font-weight: 700; color: #0f172a;">{label}</h3>
                            <button style="padding: 8px 16px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; font-weight: 600; font-size: 12px; color: #475569;">Filter</button>
                        </div>
                        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                            <thead style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                                <tr>
                                    <th style="text-align: left; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Name</th>
                                    <th style="text-align: left; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Date</th>
                                    <th style="text-align: left; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Status</th>
                                    <th style="text-align: right; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Action</th>
                                </tr>
                            </thead>
                            <tbody>{rows}</tbody>
                        </table>
                    </div>
                    '''

                elif is_app:
                    # Dashboard/App Specific Renderings
                    if ctype == "statgrid":
                        items = []
                        try: items = json.loads(content) if isinstance(content, str) else content
                        except: items = [{"label": "Metric", "value": "0"}]
                        
                        cards_html = ""
                        for item in items:
                            cards_html += f'''
                            <div class="widget col-span-3">
                                <p style="color: var(--text-secondary); font-size: 13px; font-weight: 600; text-transform: uppercase; margin-bottom: 8px;">{item.get("label")}</p>
                                <p style="font-size: 32px; font-weight: 800; color: var(--text-primary);">{item.get("value")}</p>
                                <div style="display: flex; gap: 6px; align-items: center; margin-top: 8px; font-size: 12px; color: #10b981;">
                                    <span>↑ 12%</span> <span style="color: var(--text-secondary);">vs last month</span>
                                </div>
                            </div>'''
                        section_html += f'<div class="dashboard-grid col-span-12" style="margin-bottom: 24px;">{cards_html}</div>'

                    elif ctype == "postcard":
                        section_html += f'''
                        <div class="widget col-span-8" style="margin-bottom: 24px;">
                            <div style="display: flex; gap: 16px; margin-bottom: 20px;">
                                <div class="avatar">U</div>
                                <div>
                                    <h4 style="font-weight: 700; font-size: 16px;">{label}</h4>
                                    <p style="color: var(--text-secondary); font-size: 13px;">2 hours ago • Public</p>
                                </div>
                            </div>
                            <p style="line-height: 1.6; color: #334155; margin-bottom: 20px;">{content}</p>
                            <div style="height: 240px; background: #f8fafc; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #94a3b8; font-weight: 600; font-size: 14px; margin-bottom: 20px;">
                                [Media Content Placeholder]
                            </div>
                            <div style="border-top: 1px solid #f1f5f9; padding-top: 16px; display: flex; gap: 24px;">
                                <button style="background:none; border:none; display:flex; gap:8px; align-items:center; color: #64748b; font-weight:600; font-size:13px; cursor:pointer;"><span style="font-size:18px;">♥</span> Like</button>
                                <button style="background:none; border:none; display:flex; gap:8px; align-items:center; color: #64748b; font-weight:600; font-size:13px; cursor:pointer;"><span style="font-size:18px;">💬</span> Comment</button>
                                <button style="background:none; border:none; display:flex; gap:8px; align-items:center; color: #64748b; font-weight:600; font-size:13px; cursor:pointer;"><span style="font-size:18px;">↗</span> Share</button>
                            </div>
                        </div>
                        '''

                    elif ctype == "table":
                        rows = ""
                        try:
                            data = json.loads(content) if isinstance(content, str) else content
                            for d in data[:5]:
                                rows += f'''<tr style="border-bottom: 1px solid #f1f5f9; transition: background 0.1s;">
                                    <td style="padding: 16px;">
                                        <div style="font-weight: 600; color: #1e293b;">{d.get('item', 'Item')}</div>
                                    </td>
                                    <td style="padding: 16px; color: #64748b;">{d.get('date', 'Oct 24, 2025')}</td>
                                    <td style="padding: 16px;"><span class="status-badge status-success">{d.get('status', 'Active')}</span></td>
                                    <td style="padding: 16px; text-align: right;"><a href="#" style="color: var(--primary); font-weight: 600; font-size: 13px; text-decoration: none;">Manage</a></td>
                                </tr>'''
                        except: rows = "<tr><td colspan='4' style='padding:24px; text-align:center;'>No data available</td></tr>"

                        section_html += f'''
                        <div class="widget col-span-12" style="padding: 0; overflow: hidden; margin-bottom: 24px;">
                            <div style="padding: 24px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;">
                                <h3 style="font-weight: 700; color: #0f172a;">{label}</h3>
                                <button style="padding: 8px 16px; background: white; border: 1px solid #e2e8f0; border-radius: 8px; font-weight: 600; font-size: 12px; color: #475569;">Filter</button>
                            </div>
                            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                                <thead style="background: #f8fafc; border-bottom: 1px solid #e2e8f0;">
                                    <tr>
                                        <th style="text-align: left; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Name</th>
                                        <th style="text-align: left; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Date</th>
                                        <th style="text-align: left; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Status</th>
                                        <th style="text-align: right; padding: 12px 16px; font-weight: 600; color: #475569; font-size: 12px; text-transform: uppercase;">Action</th>
                                    </tr>
                                </thead>
                                <tbody>{rows}</tbody>
                            </table>
                        </div>
                        '''

                    elif ctype == "authcard":
                        # Realistic Login/Register Form
                        is_register = "register" in label.lower() or "sign up" in label.lower()
                        title = "Create an account" if is_register else "Welcome back"
                        subtitle = "Enter your details to get started." if is_register else "Please enter your details to sign in."
                        btn_text = "Sign Up" if is_register else "Sign In"
                        switch_text = "Already have an account? Sign in" if is_register else "Don't have an account? Sign up"
                        switch_link = "login.html" if is_register else "register.html"

                        section_html += f'''
                        <div style="max-width: 400px; margin: 80px auto; padding: 40px; background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                            <div style="font-size: 24px; font-weight: 800; margin-bottom: 8px; color: #0f172a;">{title}</div>
                            <p style="color: #64748b; margin-bottom: 32px; font-size: 14px;">{subtitle}</p>
                            
                            <div style="text-align: left; margin-bottom: 16px;">
                                <label style="display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 8px;">Email Address</label>
                                <input type="email" placeholder="name@company.com" style="width: 100%; padding: 12px 16px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s;">
                            </div>
                            
                            <div style="text-align: left; margin-bottom: 24px;">
                                <label style="display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 8px;">Password</label>
                                <input type="password" placeholder="••••••••" style="width: 100%; padding: 12px 16px; border: 1px solid #e2e8f0; border-radius: 8px; font-size: 14px; outline: none; transition: border-color 0.2s;">
                            </div>
                            
                            <button class="btn btn-primary" style="width: 100%; justify-content: center; margin-bottom: 24px;">{btn_text}</button>
                            
                            <a href="{switch_link}" style="font-size: 13px; color: #64748b; text-decoration: none; font-weight: 500;">{switch_text}</a>
                        </div>
                        '''

                    else:
                        # Fallback with Smart Dummy Data
                        dummy_content = ""
                        if "feed" in label.lower() or "home" in label.lower():
                            dummy_content = f'''
                            <div style="display: flex; flex-direction: column; gap: 24px;">
                                <div class="widget">
                                    <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                                        <div class="avatar" style="background: #eff6ff; color: #3b82f6;">JD</div>
                                        <div>
                                            <div style="font-weight: 700; color: #0f172a;">John Doe</div>
                                            <div style="font-size: 12px; color: #64748b;">Product Manager • 2h ago</div>
                                        </div>
                                    </div>
                                    <p style="color: #334155; line-height: 1.6; margin-bottom: 16px;">Just launched the new version of our platform! #product #launch</p>
                                    <div style="background: #f1f5f9; height: 200px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: #94a3b8; font-weight: 600; margin-bottom: 16px;">
                                        [Image Placeholder]
                                    </div>
                                    <div style="display: flex; gap: 24px; border-top: 1px solid #f1f5f9; padding-top: 16px;">
                                        <div style="font-size: 13px; font-weight: 600; color: #64748b;">❤️ 24 Likes</div>
                                        <div style="font-size: 13px; font-weight: 600; color: #64748b;">💬 8 Comments</div>
                                    </div>
                                </div>
                            </div>
                            '''
                            section_html += f'<div class="col-span-8">{dummy_content}</div>'
                            section_html += f'''
                            <div class="col-span-4">
                                <div class="widget">
                                    <h4 style="font-weight: 700; margin-bottom: 16px;">Trending</h4>
                                    <div style="display:flex; flex-direction:column; gap:8px; color:#334155; font-size:13px;">
                                        <div>#tech</div><div>#design</div>
                                    </div>
                                </div>
                            </div>
                            '''
                        else:
                            section_html += f'''
                            <div class="widget col-span-12" style="margin-bottom: 24px;">
                                <h3 style="font-weight: 700; margin-bottom: 16px;">{label}</h3>
                                <div style="color: var(--text-secondary); line-height: 1.6;">{content}</div>
                                {f'<div style="margin-top: 24px;"><a href="{link_url}" class="btn btn-primary" style="font-size: 13px;">{subtext}</a></div>' if subtext else ''}
                            </div>
                            '''

                else:
                    # EXISTING MARKETING RENDERER LOGIC
                    if ctype == "hero":
                        section_html += f'''
                        <section class="hero">
                            <h1 style="font-size: 64px; font-weight: 900; margin-bottom: 24px; line-height: 1.1;">{label}</h1>
                            <p style="font-size: 20px; opacity: 0.8; max-width: 800px; margin: 0 auto 40px;">{content}</p>
                            <a href="{link_url}" class="btn btn-primary">{subtext}</a>
                        </section>'''
                    elif ctype == "splitsection":
                        side = "reverse" if "right" in (comp.get("annotation") or "").lower() else ""
                        section_html += f'''<section class="section-padding"><div class="split-section {side}"><div class="product-img" style="height: 500px; border-radius: var(--radius-lg);">[Visual Asset: {label}]</div><div><h2 style="font-size: 40px; font-weight: 800; margin-bottom: 24px;">{label}</h2><p style="font-size: 18px; color: var(--text-secondary); margin-bottom: 32px;">{content}</p><a href="{link_url}" class="btn btn-outline">{subtext}</a></div></div></section>'''
                    elif ctype == "productgrid":
                        section_html += f'''<section class="section-padding"><h2 style="font-size: 32px; font-weight: 800; margin-bottom: 48px;">{label}</h2><div class="grid grid-4"><div class="product-card" style="padding:24px;"><h4>Example Item</h4></div><div class="product-card" style="padding:24px;"><h4>Example Item</h4></div><div class="product-card" style="padding:24px;"><h4>Example Item</h4></div><div class="product-card" style="padding:24px;"><h4>Example Item</h4></div></div></section>'''
                    else:
                         section_html += f'''<section class="section-padding"><h2>{label}</h2><p>{content}</p></section>'''

            content_html += section_html

        # ASSEMBLY
        if is_app:
            # Build Side Navigation
            menu_items = ""
            for s in all_screens[:8]: # Limit navigation items
                active = "active" if s.get("screen", "") == wf.get("screen", "") else ""
                icon = s.get("screen", "S")[0]
                menu_items += f'<a href="{s.get("screenKey")}.html" class="menu-item {active}"><span style="width:20px; text-align:center; font-weight:bold;">{icon}</span> {s.get("screen")}</a>'

            return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen_name} - App View</title>
    <link href="https://fonts.googleapis.com/css2?family=cal_sans&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        {app_css}
        :root {{ --primary: {tokens['colors']['primary']}; --text-secondary: #64748b; --text-primary: #0f172a; --border-color: #e2e8f0; }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Inter', sans-serif; }}
        body {{ background: #f8fafc; color: #334155; }}
    </style>
</head>
<body>
    <div class="app-layout">
        <aside class="sidebar">
            <div class="sidebar-logo">
                <div style="width: 32px; height: 32px; background: var(--primary); border-radius: 8px;"></div>
                PRODUCT
            </div>
            <nav class="sidebar-menu">
                {menu_items}
            </nav>
            <div style="margin-top: auto; padding-top: 24px; border-top: 1px solid var(--border-color);">
                <div class="menu-item">
                    <div class="avatar" style="width: 32px; height: 32px; font-size: 12px;">U</div>
                    <div style="font-size: 12px; font-weight: 600;">User Account</div>
                </div>
            </div>
        </aside>
        <main class="app-main">
            <header class="top-bar">
                <h1 style="font-size: 18px; font-weight: 700; color: #0f172a;">{screen_name}</h1>
                <div style="display: flex; gap: 16px; align-items: center;">
                    <button style="width: 32px; height: 32px; border-radius: 50%; border: 1px solid #e2e8f0; background: white;">🔔</button>
                    <button class="btn btn-primary" style="padding: 8px 16px; font-size: 13px; border-radius: 6px;">+ New Action</button>
                </div>
            </header>
            <div class="page-content">
                {content_html}
            </div>
        </main>
    </div>
</body>
</html>
"""
        else:
            # RETURN ORIGINAL MARKETING SITE HTML
             return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{screen_name}</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet">
</head>
<body>
    <div class="screen-card">
        <header>
             <div class="logo">PRODUCT.</div>
             <nav class="nav-links">
                {header_links}
                <div style="width:1px; height:20px; background:var(--border-color); margin:0 8px;"></div>
                <div class="btn btn-primary" style="padding: 10px 20px; font-size: 13px;">Get Started</div>
            </nav>
        </header>
        <main>
            {content_html}
        </main>
        <footer>
            <div class="footer-grid">
                <div><div class="footer-logo">PRODUCT.</div><p>Built with Antigravity.</p></div>
                <div class="footer-col"><h4>Platform</h4><ul><li>Features</li><li>Integrations</li><li>Pricing</li></ul></div>
                <div class="footer-col"><h4>Company</h4><ul><li>About</li><li>Careers</li><li>Blog</li></ul></div>
                <div class="footer-col"><h4>Support</h4><ul><li>Docs</li><li>Contact</li><li>Status</li></ul></div>
            </div>
        </footer>
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
