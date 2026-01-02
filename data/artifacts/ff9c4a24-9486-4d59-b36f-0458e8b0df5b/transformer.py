import json
import os

def transform_layout(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    figma_data = data.get('figma', {})
    
    # Root structure as an ARRAY of Frame objects
    all_frames = []

    frame_x = 0
    frame_y = 0
    max_frame_height = 0
    frame_count = 0

    for page in figma_data.get('pages', []):
        for frame in page.get('frames', []):
            figma_frame = {
                "type": "FRAME",
                "name": frame.get('name', 'Frame'),
                "x": frame_x,
                "y": frame_y,
                "width": 1200,
                "height": 800,
                "children": [],
                "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
                "strokes": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0}}],
                "strokeWeight": 1,
                "cornerRadius": 8
            }
            
            section_y = 40
            for section in frame.get('sections', []):
                section_frame = {
                    "type": "FRAME",
                    "name": section.get('name', 'Section'),
                    "x": 40,
                    "y": section_y,
                    "width": 1120,
                    "height": 100,
                    "children": [],
                    "fills": [{"type": "SOLID", "color": {"r": 0.95, "g": 0.95, "b": 0.95}}],
                    "strokes": [{"type": "SOLID", "color": {"r": 0.8, "g": 0.8, "b": 0.8}}],
                    "strokeWeight": 1
                }
                
                # Title Text
                section_frame["children"].append({
                    "type": "TEXT",
                    "name": "Section Title",
                    "characters": section.get('name', 'Section').upper(),
                    "x": 10,
                    "y": 10,
                    "fontSize": 14,
                    "fills": [{"type": "SOLID", "color": {"r": 0.2, "g": 0.2, "b": 0.2}}]
                })
                
                comp_y = 40
                for comp in section.get('components', []):
                    # Component Rectangle
                    rect = {
                        "type": "RECTANGLE",
                        "name": comp.get('key', 'Component'),
                        "x": 20,
                        "y": comp_y,
                        "width": 1080,
                        "height": 40,
                        "fills": [{"type": "SOLID", "color": {"r": 0.9, "g": 0.9, "b": 0.9}}]
                    }
                    section_frame["children"].append(rect)
                    
                    # Component Label
                    section_frame["children"].append({
                        "type": "TEXT",
                        "name": "Component Label",
                        "characters": comp.get('key', 'Component'),
                        "x": 35,
                        "y": comp_y + 12,
                        "fontSize": 12,
                        "fills": [{"type": "SOLID", "color": {"r": 0, "g": 0, "b": 0}}]
                    })
                    
                    comp_y += 50
                
                section_frame["height"] = max(comp_y + 10, 60)
                figma_frame["children"].append(section_frame)
                section_y += section_frame["height"] + 20
            
            figma_frame["height"] = max(section_y + 20, 600)
            all_frames.append(figma_frame)
            
            # Position frames in a grid
            frame_x += 1300
            max_frame_height = max(max_frame_height, figma_frame["height"])
            frame_count += 1
            if frame_count % 4 == 0:
                frame_x = 0
                frame_y += max_frame_height + 200
                max_frame_height = 0

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_frames, f, indent=2)

if __name__ == "__main__":
    transform_layout(
        'd:/Palak/Idea-to-deploy/apps/api/data/artifacts/ff9c4a24-9486-4d59-b36f-0458e8b0df5b/docs/figma_layout.json',
        'd:/Palak/Idea-to-deploy/apps/api/data/artifacts/ff9c4a24-9486-4d59-b36f-0458e8b0df5b/docs/json_to_figma.json'
    )
