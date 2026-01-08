import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

class UIRenderer:
    def __init__(self):
        pass
    

    def render_project(self, project_id: str, wireframes: List[Dict[str, Any]], ui_design: Dict[str, Any], project_name: str = "Project"):
        from .project_manager import ARTIFACTS_DIR
        output_dir = ARTIFACTS_DIR / project_id / "ui"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        tokens = ui_design.get("design_tokens", {})
        palette = tokens.get("palette", {})
        effects = tokens.get("effects", {})
        typography = tokens.get("typography", {})
        
        # Simplified CSS
        css_template = """
:root {
    --primary: [PRIMARY];
    --bg-color: [BG_COLOR];
    --surface: [SURFACE];
    --accent: [ACCENT];
    --text-primary: [TEXT_PRIMARY];
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --radius-lg: 12px;
    --radius-md: 8px;
    --font-family: [FONT_FAMILY], sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { 
    background-color: var(--bg-color); 
    font-family: var(--font-family); 
    color: var(--text-primary); 
    line-height: 1.5; 
}

.ui-container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
.screen-card { min-height: 100vh; display: flex; flex-direction: column; }

header { 
    display: flex; justify-content: space-between; align-items: center; 
    padding: 20px 0; border-bottom: 1px solid var(--border-color);
}
.logo { font-size: 20px; font-weight: 700; display: flex; align-items: center; gap: 10px; }
.logo-icon { width: 24px; height: 24px; background: var(--primary); border-radius: 4px; }

.nav-links { display: flex; gap: 24px; align-items: center; }
.nav-links a { text-decoration: none; color: var(--text-primary); font-weight: 500; font-size: 14px; }

.section-padding { padding: 60px 0; }
.hero-split { display: grid; grid-template-columns: 1fr 1fr; gap: 40px; align-items: center; }

.grid-layout { display: grid; gap: 24px; }
.grid-cols-12 { grid-template-columns: repeat(12, 1fr); }
.col-span-12 { grid-column: span 12; }
.col-span-8 { grid-column: span 8; }
.col-span-6 { grid-column: span 6; }
.col-span-4 { grid-column: span 4; }
.col-span-3 { grid-column: span 3; }

.card { 
    background: var(--surface); border-radius: var(--radius-lg); 
    padding: 24px; border: 1px solid var(--border-color);
}

.btn { 
    padding: 12px 24px; border-radius: var(--radius-md); font-weight: 600; 
    text-decoration: none; display: inline-flex; align-items: center; 
    justify-content: center; cursor: pointer; border: none; font-size: 14px;
}
.btn-primary { background: var(--primary); color: white; }
.btn-outline { background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); }

.menu-item {
    display: flex; align-items: center; gap: 10px; padding: 10px; 
    border-radius: var(--radius-md); text-decoration: none; color: var(--text-primary); 
}
.menu-item.active { background: var(--primary); color: white; }

.input-field { border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 12px; width: 100%; outline: none; }

footer { padding: 60px 0; border-top: 1px solid var(--border-color); }
.footer-grid { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 32px; }

.app-shell { display: flex; min-height: 100vh; }
.sidebar { width: 240px; border-right: 1px solid var(--border-color); padding: 24px; }
.sidebar-menu { display: flex; flex-direction: column; gap: 8px; }
.top-bar { height: 64px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 24px; }

.avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), var(--accent)); display: flex; align-items: center; justify-content: center; font-weight: 800; }
"""
        css_content = css_template.replace("[PRIMARY]", str(palette.get('primary', '#3b82f6'))) \
                                  .replace("[BG_COLOR]", str(palette.get('background', '#ffffff'))) \
                                  .replace("[SURFACE]", str(palette.get('surface', '#f8fafc'))) \
                                  .replace("[ACCENT]", str(palette.get('accent', '#f43f5e'))) \
                                  .replace("[TEXT_PRIMARY]", str(palette.get('foreground', '#0f172a'))) \
                                  .replace("[FONT_FAMILY]", str(typography.get('body', 'sans-serif')))

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
    <title>{screen_name} | {project_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="app-shell">
            <aside class="sidebar">
                <div class="logo">
                    <div class="logo-icon"></div>
                    {project_name[:15].upper()}
                </div>
                <nav class="sidebar-menu">
                    {sidebar_menu}
                </nav>
            </aside>
            <main style="flex: 1;">
                <header class="top-bar">
                    <h1>{screen_name}</h1>
                    <div style="display: flex; gap: 12px;">
                        <div class="btn btn-outline">Search</div>
                        <div class="btn btn-primary">+ New</div>
                    </div>
                </header>
            <div class="ui-container">
                {content_html}
            </div>
        </main>
    </div>
</body>
</html>
"""
        else:
            return f"""
    <title>{screen_name} | {project_name}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="screen-card">
        <div class="ui-container">
            <header>
                <div class="logo">
                    <div class="logo-icon"></div>
                    {project_name[:20].upper()}
                </div>
                <nav class="nav-links">
                    {header_links}
                    <div class="btn btn-primary">Get Started</div>
                </nav>
            </header>
            <div>
                {content_html}
            </div>
        </div>
        <footer>
            <div class="footer-grid ui-container">
                <div>
                    <div class="logo">{project_name.upper()}</div>
                    <p>Generated by Idea-to-Deploy.</p>
                </div>
                <div>
                    <h4>Product</h4>
                    <p>Features</p>
                    <p>Pricing</p>
                </div>
                <div>
                    <h4>Support</h4>
                    <p>Help Center</p>
                    <p>Contact</p>
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

        # No heuristic type overrides or redundancy filters

        if ctype == "hero":
            return f'''
            <div class="col-span-12 section-padding">
                <div class="hero-split">
                    <div>
                        <h1 style="font-size: 48px; margin-bottom: 16px;">{label}</h1>
                        <p style="margin-bottom: 24px; opacity: 0.8;">{content}</p>
                        <div style="display: flex; gap: 12px;">
                            <a href="#" class="btn btn-primary">Get Started</a>
                            <a href="#" class="btn btn-outline">Learn More</a>
                        </div>
                    </div>
                    <div style="background: var(--surface); height: 300px; border-radius: var(--radius-lg); border: 1px solid var(--border-color);"></div>
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
             return f'''
             <div style="max-width: 400px; margin: 40px auto;">
                 <div class="card">
                    <h2 style="margin-bottom: 24px;">{label}</h2>
                    <div style="margin-bottom: 16px;">
                        <input type="email" class="input-field" placeholder="Email">
                    </div>
                    <div style="margin-bottom: 24px;">
                        <input type="password" class="input-field" placeholder="Password">
                    </div>
                    <button class="btn btn-primary" style="width:100%">{label}</button>
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
            <div class="col-span-{span}">
                <div class="card">
                   <h3 style="margin-bottom: 12px;">{label}</h3>
                   <p style="opacity:0.8; font-size:14px; margin-bottom: 16px;">{content}</p>
                   <div class="btn btn-outline" style="width: 100%;">View</div>
                </div>
            </div>
            '''
        elif ctype == "statcard":
            span = comp.get("span", 4)
            return f'''
            <div class="col-span-{span}">
                <div class="card">
                    <div style="font-size: 12px; opacity: 0.6; margin-bottom: 8px;">{label}</div>
                    <div style="font-size: 24px; font-weight: 700; color: var(--primary);">{content}</div>
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
                 items = []
             
             cards_html = ""
             for item in items:
                 i_title = item.get("title", "Feature") if isinstance(item, dict) else str(item)
                 i_desc = item.get("desc", item.get("description", "Experience the power of our platform with this cutting-edge feature designed for growth.")) if isinstance(item, dict) else "Detailed feature description goes here."
                 
                 cards_html += f'''
                 <div class="card" style="padding: 40px;">
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
                        {rows_html}
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
